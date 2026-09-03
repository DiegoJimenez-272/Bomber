import os
import re
import uuid
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

ALLOWED_DOCUMENT_EXTENSIONS = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.png', '.jpg', '.jpeg', '.txt', '.csv', '.zip', '.rar']
ALLOWED_IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.webp']

MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB máximo para documentos
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024     # 5 MB máximo para imágenes

MAGIC_SIGNATURES = {
    '.pdf': [b'%PDF-'],
    '.png': [b'\x89PNG\r\n\x1a\n'],
    '.jpg': [b'\xff\xd8\xff'],
    '.jpeg': [b'\xff\xd8\xff'],
    '.webp': [b'RIFF'],
    '.zip': [b'PK\x03\x04'],
    '.docx': [b'PK\x03\x04'],
    '.xlsx': [b'PK\x03\x04'],
    '.pptx': [b'PK\x03\x04'],
}

RUTS_PRUEBA_CONOCIDOS = {
    '111111111', '222222222', '333333333', '444444444',
    '555555555', '666666666', '777777777', '888888888',
    '999999999', '000000000', '876543210'
}


def es_rut_persona_natural_valido(rut: str) -> tuple[bool, str]:
    """
    Valida de forma exhaustiva que un RUT corresponda a una persona natural real:
    1. Verifica que no corresponda a secuencias repetitivas ni RUTs de prueba conocidos.
    2. Aplica filtro de rangos lógicos para personas naturales en Chile (1.000.000 a 50.000.000).
    3. Valida el dígito verificador mediante el algoritmo del Módulo 11.
    Retorna una tupla (es_valido, mensaje_error).
    """
    if not isinstance(rut, str):
        return False, "El RUT ingresado no es válido."

    rut_limpio = re.sub(r'[^0-9kK]', '', rut).upper()

    if len(rut_limpio) < 2 or len(rut_limpio) > 10:
        return False, "El RUT ingresado no tiene un largo válido."

    cuerpo = rut_limpio[:-1]
    dv_ingresado = rut_limpio[-1]

    if not cuerpo.isdigit():
        return False, "El cuerpo del RUT debe contener únicamente números."

    # 1. Detección de RUTs de prueba y secuencias de dígitos repetidos
    if len(set(cuerpo)) == 1:
        return False, "No se permiten RUTs de prueba formados por un solo dígito repetido."

    if rut_limpio in RUTS_PRUEBA_CONOCIDOS:
        return False, "El RUT ingresado corresponde a un número de prueba no permitido."

    # 2. Filtro de rangos lógicos para personas naturales
    cuerpo_num = int(cuerpo)
    if cuerpo_num < 1_000_000:
        return False, "El RUT ingresado es inferior al rango mínimo de personas naturales."
    if cuerpo_num > 50_000_000:
        return False, "El RUT ingresado corresponde a una persona jurídica o empresa (serie 50M+), no a una persona natural."

    # 3. Algoritmo Módulo 11
    suma = 0
    multiplicador = 2

    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = 2 if multiplicador == 7 else multiplicador + 1

    resto = 11 - (suma % 11)

    if resto == 11:
        dv_calculado = '0'
    elif resto == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(resto)

    if dv_calculado != dv_ingresado:
        return False, "El RUT ingresado no es válido. Revisa el número y el dígito verificador."

    return True, ""


def validar_rut(rut: str) -> bool:
    """
    Función booleana de verificación de RUT.
    """
    es_valido, _ = es_rut_persona_natural_valido(rut)
    return es_valido


def formatear_rut(rut: str) -> str:
    """
    Formatea un RUT al estándar chileno: XX.XXX.XXX-X
    """
    if not rut:
        return rut
    rut_limpio = re.sub(r'[^0-9kK]', '', str(rut)).upper()
    if len(rut_limpio) < 2:
        return rut
    cuerpo = rut_limpio[:-1]
    dv = rut_limpio[-1]
    cuerpo_formateado = f"{int(cuerpo):,}".replace(",", ".")
    return f"{cuerpo_formateado}-{dv}"


def validar_rut_chileno(value):
    """
    Validador nativo de Django para verificar el RUT chileno con mensajes específicos.
    """
    if value:
        es_valido, msg = es_rut_persona_natural_valido(value)
        if not es_valido:
            raise ValidationError(msg)


def validar_extension_archivo(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_DOCUMENT_EXTENSIONS:
        raise ValidationError(f"Formato de archivo '{ext}' no permitido. Extensiones permitidas: {', '.join(ALLOWED_DOCUMENT_EXTENSIONS)}")
    
    if value.size > MAX_DOCUMENT_SIZE_BYTES:
        raise ValidationError("El archivo excede el tamaño máximo permitido de 10 MB.")
    
    if ext in MAGIC_SIGNATURES:
        value.seek(0)
        header = value.read(16)
        value.seek(0)
        
        valid_magic = any(header.startswith(sig) for sig in MAGIC_SIGNATURES[ext])
        if not valid_magic:
            raise ValidationError(f"El contenido real del archivo no coincide con la extensión declarada '{ext}'.")

def validar_extension_imagen(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(f"Formato de imagen '{ext}' no permitido. Extensiones permitidas: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}")
    
    if value.size > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError("La imagen excede el tamaño máximo permitido de 5 MB.")
    
    if ext in MAGIC_SIGNATURES:
        value.seek(0)
        header = value.read(16)
        value.seek(0)
        
        valid_magic = any(header.startswith(sig) for sig in MAGIC_SIGNATURES[ext])
        if not valid_magic:
            raise ValidationError(f"El contenido binario de la imagen no coincide con el formato '{ext}'.")

@deconstructible
class SecureFilePath:
    def __init__(self, subfolder):
        self.subfolder = subfolder

    def __call__(self, instance, filename):
        ext = os.path.splitext(filename)[1].lower()
        new_filename = f"{uuid.uuid4().hex}{ext}"
        return os.path.join(self.subfolder, new_filename)
