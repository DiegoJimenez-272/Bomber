from django.db import migrations, models


def crear_configuracion_inicial(apps, schema_editor):
    Guia = apps.get_model('usuarios', 'GuiaChatbot')
    Comando = apps.get_model('usuarios', 'ComandoChatbot')

    guias = [
        {
            'titulo': 'Consultar el inventario',
            'palabras_clave': 'inventario, equipos, materiales, bodega, buscar equipo',
            'pasos': '1. Abre Inventario desde el menú lateral.\n2. Selecciona la compañía si tienes acceso global.\n3. Usa el buscador para filtrar por nombre, usuario asignado o ubicación.',
            'modulo': 'inventario',
        },
        {
            'titulo': 'Registrar una emergencia',
            'palabras_clave': 'registrar emergencia, crear emergencia, nueva emergencia',
            'pasos': '1. Abre Emergencias desde el menú lateral.\n2. Completa el formulario de registro y selecciona el personal participante.\n3. Guarda el registro como incompleto o finalízalo según corresponda.',
            'modulo': 'emergencias',
        },
        {
            'titulo': 'Registrar una salida a terreno',
            'palabras_clave': 'salida a terreno, registrar salida, nueva salida, salida de carro',
            'pasos': '1. Abre Salidas a Terreno desde el menú lateral.\n2. Selecciona Registrar Salida.\n3. Completa los datos del recorrido y guarda el registro.',
            'modulo': 'salidas',
        },
        {
            'titulo': 'Consultar los movimientos de caja',
            'palabras_clave': 'movimientos de caja, consultar caja, historial caja, caja chica',
            'pasos': '1. Abre Caja desde el menú lateral.\n2. Revisa el historial de movimientos y utiliza los filtros disponibles.',
            'modulo': 'caja',
        },
    ]
    for guia in guias:
        Guia.objects.get_or_create(titulo=guia['titulo'], defaults=guia)

    comandos = [
        {
            'nombre': 'Resumen de inventario',
            'palabras_clave': 'resumen de inventario, stock, cantidad de equipos, ítems en bodega',
            'handler': 'inventario_resumen',
            'modulo_requerido': 'inventario',
        },
        {
            'nombre': 'Emergencias activas',
            'palabras_clave': 'emergencias activas, emergencia activa, incendios activos',
            'handler': 'emergencias_activas',
            'modulo_requerido': 'emergencias',
        },
        {
            'nombre': 'Saldo de caja',
            'palabras_clave': 'saldo de caja, saldo caja, saldo actual caja',
            'handler': 'caja_saldo',
            'modulo_requerido': 'caja',
        },
    ]
    for comando in comandos:
        Comando.objects.get_or_create(nombre=comando['nombre'], defaults=comando)


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0052_reporte_error'),
    ]

    operations = [
        migrations.CreateModel(
            name='ComandoChatbot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=120, unique=True)),
                ('palabras_clave', models.TextField(help_text='Separa las palabras o frases con coma o una línea nueva.')),
                ('handler', models.CharField(choices=[('inventario_resumen', 'Resumen de inventario'), ('emergencias_activas', 'Emergencias activas'), ('caja_saldo', 'Saldo de caja')], max_length=40)),
                ('modulo_requerido', models.CharField(choices=[('inventario', 'Inventario'), ('emergencias', 'Emergencias'), ('caja', 'Caja')], max_length=24)),
                ('prioridad', models.PositiveSmallIntegerField(default=0)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Comando de consulta del chatbot',
                'verbose_name_plural': 'Comandos de consulta del chatbot',
                'ordering': ['-prioridad', 'nombre'],
            },
        ),
        migrations.CreateModel(
            name='GuiaChatbot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=160)),
                ('palabras_clave', models.TextField(help_text='Separa las palabras o frases con coma o una línea nueva.')),
                ('pasos', models.TextField(help_text='Instrucciones breves, una por línea.')),
                ('modulo', models.CharField(choices=[('dashboard', 'Inicio'), ('inventario', 'Inventario'), ('emergencias', 'Emergencias'), ('salidas', 'Salidas a terreno'), ('caja', 'Caja'), ('documentos', 'Documentos'), ('capacitaciones', 'Cursos y capacitaciones'), ('malla', 'Malla curricular'), ('mantenimiento', 'Mantenimiento'), ('proyectos', 'Proyectos')], default='dashboard', max_length=24)),
                ('prioridad', models.PositiveSmallIntegerField(default=0)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Guía del chatbot',
                'verbose_name_plural': 'Guías del chatbot',
                'ordering': ['-prioridad', 'titulo'],
            },
        ),
        migrations.RunPython(crear_configuracion_inicial, migrations.RunPython.noop),
    ]
