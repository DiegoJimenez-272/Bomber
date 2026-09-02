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

def validar_rut(rut: str) -> bool:
    """
    Valida un RUT chileno aplicando el algoritmo oficial del Módulo 11.
    Acepta cualquier formato (con o sin puntos, guiones o espacios).
    """
    if not isinstance(rut, str):
        return False

    rut_limpio = re.sub(r'[^0-9kK]', '', rut).upper()

    if len(rut_limpio) < 2 or len(rut_limpio) > 10:
        return False

    cuerpo = rut_limpio[:-1]
    dv_ingresado = rut_limpio[-1]

    if not cuerpo.isdigit():
        return False

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

    return dv_calculado == dv_ingresado


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
    Validador nativo de Django para verificar el RUT chileno.
    """
    if value and not validar_rut(value):
        raise ValidationError("El RUT ingresado no es válido. Revisa el número y el dígito verificador.")


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
