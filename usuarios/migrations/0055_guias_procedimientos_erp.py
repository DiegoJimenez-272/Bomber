from django.db import migrations, models


def cargar_guias(apps, schema_editor):
    Guia = apps.get_model('usuarios', 'GuiaChatbot')
    guias = [
        (
            'Crear un documento redactado',
            'crear documento, nuevo documento, redactar documento, crear pdf, generar documento, escribir documento',
            '1. Abre Documentos.\n2. Pulsa “Redactar Documento”.\n3. Completa el título y el contenido; la descripción, clasificación y carpeta son opcionales.\n4. Pulsa “Guardar Documento”; el sistema genera un PDF.\nNecesitas permiso para editar Documentos.',
            'documentos', 10,
        ),
        (
            'Subir un archivo a Documentos',
            'subir documento, subir archivo, cargar archivo, adjuntar documento, agregar archivo a documentos',
            '1. Abre Documentos y pulsa “Subir Documento”.\n2. Escribe el nombre, elige la clasificación y selecciona el archivo.\n3. Si quieres, elige una carpeta y marca si será privado.\n4. Pulsa “Subir”.\nNecesitas permiso para editar Documentos.',
            'documentos', 9,
        ),
        (
            'Crear una carpeta de documentos',
            'crear carpeta documentos, nueva carpeta, organizar documentos, carpeta nueva',
            '1. Abre Documentos y pulsa “Crear Carpeta”.\n2. Escribe el nombre y define si será privada.\n3. Los superusuarios también pueden asignarla a una compañía.\n4. Pulsa “Crear”.\nNecesitas permiso para editar Documentos.',
            'documentos', 8,
        ),
        (
            'Agregar ítems al inventario',
            'agregar item inventario, agregar equipo, crear item, registrar material, nuevo equipo, ingresar equipo a bodega',
            '1. Abre Inventario y, si tienes acceso global, selecciona la compañía.\n2. Pulsa “Agregar Ítem”.\n3. Completa nombre, cantidad, ubicación y estado.\n4. Completa fecha y valor si corresponde, y pulsa “Guardar Ítem”.\nNecesitas permiso para editar Inventario.',
            'inventario', 9,
        ),
        (
            'Buscar equipos en inventario',
            'buscar equipo, encontrar item, filtrar inventario, consultar material, revisar bodega',
            '1. Abre Inventario.\n2. Selecciona la compañía si tienes acceso global.\n3. Escribe en el buscador el nombre del ítem, usuario asignado o ubicación.',
            'inventario', 7,
        ),
        (
            'Registrar una emergencia',
            'registrar emergencia, registro emergencia, registrar un incendio, crear emergencia, nueva emergencia, reportar rescate',
            '1. Abre Emergencias y pulsa “Registrar Emergencia”.\n2. Completa tipo, dirección, fecha y hora, estado, unidades y oficial a cargo según corresponda.\n3. Agrega los detalles del incidente y selecciona el personal asistente por unidad.\n4. Adjunta un documento si lo necesitas.\n5. Usa “Guardar sin completar” para dejarla pendiente o “Finalizar Registro” para completarla.\nNecesitas permiso para editar Emergencias.',
            'emergencias', 10,
        ),
        (
            'Marcar asistencia por unidad en una emergencia',
            'asistencia emergencia, asistentes emergencia, personal asistente, marcar bomberos emergencia, bomberos participantes emergencia',
            '1. En el formulario de Emergencias, agrega o selecciona cada unidad despachada.\n2. Abre “Editar asistencia” en esa unidad.\n3. Busca y marca a los bomberos participantes.\n4. Pulsa “Guardar asistencia” y luego guarda la emergencia.\nUna persona no debe quedar asignada a distintos carros.',
            'emergencias', 8,
        ),
        (
            'Registrar una salida a terreno',
            'registrar salida, crear salida terreno, nueva salida, salida de carro, registrar recorrido',
            '1. Abre Salidas a Terreno y pulsa “Registrar Salida”.\n2. Completa motivo, dirección, fecha y hora, kilometraje de salida y personal a cargo.\n3. Agrega las unidades y marca la asistencia de cada una.\n4. Guarda el registro. Al regresar, completa el kilometraje de regreso.',
            'salidas', 9,
        ),
        (
            'Registrar un movimiento de caja',
            'registrar movimiento caja, nuevo ingreso, nuevo egreso, registrar gasto, registrar ingreso caja, comprobante caja',
            '1. Abre Caja y pulsa “Nuevo Movimiento”.\n2. Selecciona primero el tipo de movimiento y luego la caja a asignar, si tienes esa opción.\n3. Elige tipo de cuenta, monto y descripción.\n4. Adjunta el comprobante requerido y pulsa “Guardar Movimiento”.\nNecesitas permiso para editar Caja.',
            'caja', 9,
        ),
        (
            'Asignar voluntarios a un ramo',
            'asignar voluntario ramo, inscribir voluntario, agregar usuario malla, cursar ramo, asignar alumnos curso malla',
            '1. Abre Malla Curricular y busca el ramo.\n2. Pulsa “Asignar voluntarios”.\n3. Busca y marca a los voluntarios que cursarán el ramo.\n4. Pulsa “Guardar asignación”.\nNecesitas permiso para editar la Malla Curricular.',
            'malla', 9,
        ),
        (
            'Registrar una actividad de capacitación',
            'crear capacitacion, registrar curso, nueva actividad, crear actividad, agendar capacitacion',
            '1. Abre Cursos y Capacitaciones.\n2. Pulsa la opción para registrar una nueva actividad.\n3. Completa los datos de la actividad y selecciona compañías y participantes.\n4. Pulsa “Guardar Actividad”.\nNecesitas permiso para editar Cursos y Capacitaciones.',
            'capacitaciones', 8,
        ),
        (
            'Registrar un mantenimiento',
            'crear mantenimiento, registrar mantenimiento, nuevo mantenimiento, revision carro, registrar reparacion',
            '1. Abre Mantenimiento y pulsa “Nuevo Mantenimiento”.\n2. Completa los datos del vehículo y del trabajo realizado.\n3. Añade documentos si corresponde y pulsa “Guardar Mantenimiento”.\nNecesitas permiso para editar Mantenimiento.',
            'mantenimiento', 8,
        ),
        (
            'Crear un proyecto',
            'crear proyecto, nuevo proyecto, registrar proyecto, agregar proyecto',
            '1. Abre Proyectos y pulsa “Nuevo Proyecto”.\n2. Completa el formulario con la información del proyecto.\n3. Pulsa “Crear Proyecto”.\nNecesitas permiso para editar Proyectos.',
            'proyectos', 8,
        ),
        (
            'Escanear el código QR de un equipo',
            'escanear codigo qr, leer qr equipo, buscar equipo por qr, identificar item qr',
            '1. Abre Escanear QR desde el menú lateral.\n2. Autoriza el acceso a la cámara o selecciona la opción de escaneo disponible.\n3. Enfoca el código QR del equipo para abrir su ficha.\nNecesitas permiso para Escanear QR.',
            'qr', 8,
        ),
        (
            'Crear un usuario desde Administración',
            'crear usuario, nuevo usuario, agregar bombero, registrar usuario sistema, crear cuenta usuario',
            '1. Abre Administración y entra en la sección de usuarios.\n2. Pulsa “Crear Nuevo Usuario”.\n3. Completa sus datos, compañía, rol y credenciales, y guarda.\nNecesitas ser superusuario.',
            'administracion', 8,
        ),
        (
            'Crear un rol y configurar permisos',
            'crear rol, nuevo rol, configurar permisos, permisos de usuario, agregar rol',
            '1. Abre Administración y la sección de roles.\n2. Pulsa “Crear Rol”, define el nombre y marca los permisos de módulos y edición.\n3. Guarda el rol y asígnalo a los usuarios correspondientes.\nNecesitas ser superusuario.',
            'administracion', 8,
        ),
        (
            'Crear una compañía',
            'crear compañia, crear compañía, nueva compañia, agregar compañía, registrar compañía',
            '1. Abre Administración y la sección de compañías.\n2. Pulsa “Crear Nueva Compañía”.\n3. Completa el nombre y la ubicación, agrega el logo si corresponde y guarda.\nNecesitas ser superusuario.',
            'administracion', 7,
        ),
    ]

    for titulo, palabras, pasos, modulo, prioridad in guias:
        Guia.objects.get_or_create(
            titulo=titulo,
            defaults={
                'palabras_clave': palabras,
                'pasos': pasos,
                'modulo': modulo,
                'prioridad': prioridad,
                'activo': True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0054_guia_consultar_emergencias'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guiachatbot',
            name='modulo',
            field=models.CharField(choices=[
                ('dashboard', 'Inicio'),
                ('inventario', 'Inventario'),
                ('emergencias', 'Emergencias'),
                ('salidas', 'Salidas a terreno'),
                ('caja', 'Caja'),
                ('documentos', 'Documentos'),
                ('capacitaciones', 'Cursos y capacitaciones'),
                ('malla', 'Malla curricular'),
                ('mantenimiento', 'Mantenimiento'),
                ('proyectos', 'Proyectos'),
                ('resumen', 'Resumen General'),
                ('inspectores', 'Inspectores'),
                ('qr', 'Escanear QR'),
                ('administracion', 'Administración'),
            ], default='dashboard', max_length=24),
        ),
        migrations.RunPython(cargar_guias, migrations.RunPython.noop),
    ]
