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
    'resumen': ('ver_resumen_general', 'dashboard_summary'),
    'inventario': ('ver_inventario', 'inventario'),
    'emergencias': ('ver_emergencias', 'emergencias'),
    'salidas': ('ver_salidas_terreno', 'salidas_terreno'),
    'caja': ('ver_caja_chica', 'caja_chica'),
    'documentos': ('ver_documentacion', 'documentos'),
    'capacitaciones': ('ver_capacitaciones', 'capacitaciones'),
    'malla': ('ver_malla_curricular', 'malla_curricular'),
    'mantenimiento': ('ver_mantenimientos', 'mantenimiento'),
    'proyectos': ('ver_proyectos', 'proyectos'),
    'inspectores': ('__inspector__', 'inspectores'),
    'qr': ('ver_escanear_qr', 'scan_qr_page'),
    'administracion': ('__superuser__', 'administracion'),
}
MODULO_LABELS = {
    'dashboard': 'Inicio',
    'resumen': 'Resumen General',
    'inventario': 'Inventario',
    'emergencias': 'Emergencias',
    'salidas': 'Salidas a Terreno',
    'caja': 'Caja',
    'documentos': 'Documentos',
    'capacitaciones': 'Cursos y Capacitaciones',
    'malla': 'Malla Curricular',
    'mantenimiento': 'Mantenimiento',
    'proyectos': 'Proyectos',
    'inspectores': 'Inspectores',
    'qr': 'Escanear QR',
    'administracion': 'Administración',
}

# Orientación general para los módulos. Las instrucciones específicas siguen
# siendo editables en GuiaChatbot y tienen prioridad sobre estas respuestas.
TOPIC_FALLBACKS = [
    ('inventario', 'inventario, equipo, equipos, material, materiales, stock, bodega, casco, herramienta', 'En Inventario puedes consultar equipos, buscar por nombre o ubicación y revisar sus asignaciones.'),
    ('emergencias', 'emergencia, emergencias, incendio, incendios, rescate, accidente, siniestro', 'En Emergencias puedes revisar los registros y sus filtros. Para registrar una nueva, abre el formulario del módulo.'),
    ('salidas', 'salida, salidas, terreno, kilometraje, recorrido, carro, unidad despachada', 'En Salidas a Terreno puedes registrar recorridos, unidades, personal y kilometrajes, y revisar el historial.'),
    ('caja', 'caja, saldo, ingreso, egreso, gasto, gastos, movimiento, movimientos, cuenta bancaria', 'En Caja puedes consultar movimientos y saldos. Los movimientos registran ingresos o egresos y su tipo de cuenta.'),
    ('documentos', 'documento, documentos, archivo, archivos, carpeta, informe', 'Para agregar un documento: 1. Abre Documentos. 2. Pulsa “Subir Documento”. 3. Escribe el nombre, selecciona la clasificación y el archivo. 4. Si quieres, elige una carpeta y marca si será privado. 5. Pulsa “Subir”. Para redactarlo dentro del sistema y generar un PDF, usa “Redactar Documento”. Necesitas permiso de edición de documentos.'),
    ('capacitaciones', 'curso, cursos, capacitacion, capacitaciones, entrenamiento, reunion', 'En Cursos y Capacitaciones puedes revisar actividades y registros de formación.'),
    ('malla', 'malla curricular, malla, ramo, ramos, asignatura, asignaturas', 'En Malla Curricular puedes revisar los ramos y, según tus permisos, gestionar voluntarios inscritos.'),
    ('mantenimiento', 'mantenimiento, mantencion, mantenciones, revision vehicular, reparacion', 'En Mantenimiento puedes consultar los registros de mantenimiento de vehículos.'),
    ('proyectos', 'proyecto, proyectos, presupuesto, presupuestos', 'En Proyectos puedes consultar el seguimiento y la información de los proyectos.'),
    ('resumen', 'resumen general, resumen, indicadores, kpi, estadisticas, estadistica', 'El Resumen General presenta indicadores y actividad del sistema.'),
    ('inspectores', 'inspector, inspectores, inspeccion, inspecciones', 'El módulo Inspectores reúne documentos y archivos disponibles para inspectores.'),
    ('qr', 'qr, codigo qr, escanear qr, escaner', 'Escanear QR permite identificar un ítem de inventario mediante su código.'),
    ('administracion', 'administracion, usuarios, roles, companias, permisos', 'Administración permite gestionar usuarios, roles y compañías; está disponible solo para superusuarios.'),
]

CONSULTAS_SOLO_ADMIN = (
    'administracion, panel administrativo, crear usuario, nuevo usuario, crear usuarios, nuevo usuario',
    'gestionar usuarios, administrar usuarios, editar usuario, editar usuarios, eliminar usuario, eliminar usuarios',
    'crear rol, nuevo rol, administrar roles, gestionar roles, configurar permisos, permisos de usuario',
    'crear compania, nueva compania, administrar companias, gestionar companias',
)

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
    if requisito == '__superuser__':
        return bool(user.is_superuser)
    if requisito == '__inspector__':
        return bool(getattr(user, 'es_inspector', False))
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
    tokens = [token for token in texto.split() if token not in STOPWORDS]
    mejor = 0
    for clave in entradas:
        clave_tokens = [token for token in clave.split() if token not in STOPWORDS]
        if not clave_tokens:
            continue

        def tokens_compatibles(a, b):
            # Tolera plurales y conjugaciones frecuentes sin instalar librerías NLP.
            return a == b or (min(len(a), len(b)) >= 4 and a[:4] == b[:4])

        coincide = any(tokens_compatibles(palabra, token) for palabra in clave_tokens for token in tokens)
        frase_coincide = any(
            all(tokens_compatibles(esperada, recibida) for esperada, recibida in zip(clave_tokens, tokens[indice:indice + len(clave_tokens)]))
            for indice in range(max(0, len(tokens) - len(clave_tokens) + 1))
        )
        if frase_coincide:
            mejor = max(mejor, sum(map(len, clave_tokens)) + 2)
        elif coincide and len(clave_tokens) == 1:
            mejor = max(mejor, len(clave_tokens[0]))
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

    # Administración solo es visible para superusuarios en el ERP. Este bloqueo
    # explícito evita responder sobre esas pantallas incluso si una guía se
    # etiqueta por error con otro módulo.
    if not user.is_superuser and _coincidencia(texto, _palabras(','.join(CONSULTAS_SOLO_ADMIN))):
        return {'text': 'No puedo responder esa consulta con los permisos de tu cuenta.'}

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

    mejor_modulo = None
    mejor_puntaje = 0
    for modulo, palabras, respuesta in TOPIC_FALLBACKS:
        if not _puede_ver_modulo(user, modulo):
            continue
        puntaje = _coincidencia(texto, _palabras(palabras))
        if puntaje > mejor_puntaje:
            mejor_modulo = (modulo, respuesta)
            mejor_puntaje = puntaje
    if mejor_modulo:
        modulo, respuesta = mejor_modulo
        _, ruta = MODULOS[modulo]
        try:
            url = reverse(ruta)
        except Exception:
            url = None
        return {
            'text': respuesta,
            'url': url,
            'label': f'Abrir {MODULO_LABELS.get(modulo, modulo)}' if url else None,
        }

    modulos_visibles = [
        MODULO_LABELS.get(modulo, modulo)
        for modulo in MODULOS if _puede_ver_modulo(user, modulo)
    ]
    disponibles = ', '.join(modulos_visibles) or 'los módulos habilitados para tu cuenta'
    return {'text': f'Puedo orientarte sobre estos módulos: {disponibles}. Pregunta por uno de ellos o por una acción específica.'}
