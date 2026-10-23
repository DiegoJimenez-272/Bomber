"""Motor de respuestas por reglas del ERP.

Los datos de la BD solo eligen un handler de esta lista permitida; nunca se
evalúan como Python, SQL ni rutas libres.
"""
import re
import unicodedata

from django.db.models import Q, Sum, Case, When, F, DecimalField
from django.urls import reverse

from .inventory_permissions import puede_gestionar_inventario_global
from .models import CajaChica, Emergencia, GuiaChatbot, Inventario, ComandoChatbot


MODULOS = {
    'dashboard': (None, 'dashboard'),
    'inventario': ('ver_inventario', 'inventario'),
    'emergencias': ('ver_emergencias', 'emergencias'),
    'salidas': ('ver_salidas_terreno', 'salidas_terreno'),
    'caja': ('ver_caja_chica', 'caja_chica'),
    'documentos': ('ver_documentacion', 'documentos'),
    'capacitaciones': ('ver_capacitaciones', 'capacitaciones'),
    'malla': ('ver_malla_curricular', 'malla_curricular'),
    'mantenimiento': ('ver_mantenimientos', 'mantenimiento'),
    'proyectos': ('ver_proyectos', 'proyectos'),
}

STOPWORDS = {
    'a', 'al', 'como', 'de', 'del', 'el', 'en', 'es', 'esta', 'este', 'hay',
    'la', 'las', 'lo', 'los', 'me', 'mi', 'para', 'por', 'que', 'se', 'un',
    'una', 'unas', 'unos', 'y', 'donde', 'puedo', 'quiero', 'necesito',
}


def normalizar(texto):
    texto = unicodedata.normalize('NFD', texto.casefold())
    texto = ''.join(caracter for caracter in texto if unicodedata.category(caracter) != 'Mn')
    return ' '.join(re.findall(r'[a-z0-9]+', texto))


def _palabras(configuracion):
    return [normalizar(valor) for valor in re.split(r'[,\n;]+', configuracion or '') if normalizar(valor)]


def _puede_ver_modulo(user, modulo):
    requisito, _ = MODULOS.get(modulo, (None, None))
    if requisito is None:
        return modulo == 'dashboard'
    if user.is_superuser:
        return True
    rol = getattr(user, 'rol', None)
    return bool(rol and getattr(rol, requisito, False))


def _url_modulo(modulo):
    configuracion = MODULOS.get(modulo)
    if not configuracion:
        return None
    try:
        return reverse(configuracion[1])
    except Exception:
        return None


def _coincidencia(texto, entradas):
    tokens = set(texto.split()) - STOPWORDS
    texto_sin_stopwords = ' '.join(token for token in texto.split() if token not in STOPWORDS)
    mejor = 0
    for clave in entradas:
        clave_sin_stopwords = ' '.join(token for token in clave.split() if token not in STOPWORDS)
        if ' ' in clave_sin_stopwords and clave_sin_stopwords in texto_sin_stopwords:
            mejor = max(mejor, len(clave_sin_stopwords) + 2)
        elif clave_sin_stopwords in tokens:
            mejor = max(mejor, len(clave_sin_stopwords))
    return mejor


def _buscar_configuracion(texto, queryset):
    mejor = None
    mejor_puntaje = 0
    for registro in queryset:
        puntaje = _coincidencia(texto, _palabras(registro.palabras_clave))
        if puntaje > mejor_puntaje:
            mejor, mejor_puntaje = registro, puntaje
    return mejor


def _lookup_inventario(user):
    items = Inventario.objects.all()
    acceso_global = puede_gestionar_inventario_global(user)
    if not acceso_global:
        if not user.compania_id:
            return {'text': 'Tu cuenta no tiene una compañía asignada para consultar el inventario.'}
        items = items.filter(compania_id=user.compania_id)
    total = items.count()
    bodega = items.filter(asignado_a__isnull=True, asignado_a_vehiculo__isnull=True).count()
    alcance = 'todas las compañías' if acceso_global else user.compania.nombre
    return {'text': f'Inventario de {alcance}: {total} ítems registrados; {bodega} sin asignar.'}


def _lookup_emergencias(user):
    emergencias = Emergencia.objects.filter(estado='Activa').count()
    return {'text': f'Actualmente hay {emergencias} emergencia(s) activa(s).', 'url': _url_modulo('emergencias'), 'label': 'Abrir Emergencias'}


def _lookup_caja(user):
    movimientos = CajaChica.objects.all()
    if not user.is_superuser:
        if not user.compania_id:
            return {'text': 'Tu cuenta no tiene una compañía asignada para consultar el saldo de caja.'}
        movimientos = movimientos.filter(compania_id=user.compania_id)
    saldo = movimientos.aggregate(saldo=Sum(Case(
        When(tipo='Ingreso', then=F('monto')),
        When(tipo='Egreso', then=-F('monto')),
        output_field=DecimalField(max_digits=14, decimal_places=2),
    )))['saldo'] or 0
    return {'text': f'Saldo actual de caja: ${saldo:,.0f} CLP.', 'url': _url_modulo('caja'), 'label': 'Abrir Caja'}


HANDLERS = {
    'inventario_resumen': _lookup_inventario,
    'emergencias_activas': _lookup_emergencias,
    'caja_saldo': _lookup_caja,
}


def responder(user, mensaje):
    texto = normalizar(mensaje)
    if not texto:
        return {'text': 'Escribe una pregunta para poder ayudarte.'}

    comandos = [
        comando for comando in ComandoChatbot.objects.filter(activo=True).order_by('-prioridad', 'id')
        if _puede_ver_modulo(user, comando.modulo_requerido)
        and comando.handler in HANDLERS
    ]
    comando = _buscar_configuracion(texto, comandos)
    if comando:
        return HANDLERS[comando.handler](user)

    guias = [
        guia for guia in GuiaChatbot.objects.filter(activo=True).order_by('-prioridad', 'titulo')
        if _puede_ver_modulo(user, guia.modulo)
    ]
    guia = _buscar_configuracion(texto, guias)
    if guia:
        url = _url_modulo(guia.modulo)
        return {
            'text': f'{guia.titulo}\n{guia.pasos}',
            'url': url,
            'label': f'Abrir {guia.get_modulo_display()}' if url else None,
        }

    return {'text': 'No encontré una guía o consulta para esa pregunta. Prueba con palabras como “inventario”, “emergencias activas” o “saldo de caja”.'}
