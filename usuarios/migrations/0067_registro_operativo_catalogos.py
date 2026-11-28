from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


TIPOS = [
    ('emergencia', 'Emergencia'),
    ('emergencia_vehicular', 'Emergencia vehicular (10-4)'),
    ('servicio_especial', 'Servicio especial'),
    ('practica_maquinista', 'Práctica de aspirante a maquinista (6-18)'),
    ('rodaje', 'Rodaje'),
    ('se_dirige_6_13', 'Se dirige a (6-13)'),
    ('rodaje_6_13', 'Registro histórico: Se dirige a (6-13) — Rodaje'),
    ('combustible_6_14', 'Carga de combustible (6-14)'),
    ('ronda_maquinistas', 'Ronda de maquinistas'),
    ('llegada_cuartel', 'Voluntarios llegados al cuartel'),
]

EMERGENCIA_CHOICES = [
    ('10-0', '10-0 — Llamado estructural'),
    ('10-0-1', '10-0-1 — Incendio estructural'),
    ('10-0-2', '10-0-2 — Edificio de cuatro o más pisos'),
    ('10-0-3', '10-0-3 — Lugar público en horario de funcionamiento'),
    ('10-0-4', '10-0-4 — Incendio estructural industrial'),
    ('10-0-5', '10-0-5 — Incendio estructural Hazmat'),
    ('10-0-15', '10-0-15 — Incendio rural'),
    ('10-0-7', '10-0-7 — Inflamación de ducto'),
    ('10-1-1', '10-1-1 — Incendio vehicular menor'),
    ('10-1-2', '10-1-2 — Incendio de vehículo de carga'),
    ('10-1-3', '10-1-3 — Incendio de vehículo con pasajeros'),
    ('10-1-4', '10-1-4 — Incendio de maquinaria agrícola, pesada o forestal'),
    ('10-1-5', '10-1-5 — Incendio de aeronave'),
    ('10-1-6', '10-1-6 — Incendio en vehículo a gas'),
    ('10-1-7', '10-1-7 — Incendio en vehículo eléctrico'),
    ('10-2-1', '10-2-1 — Incendio de pastizal urbano'),
    ('10-2-2', '10-2-2 — Incendio de pastizal rural'),
    ('10-2-3', '10-2-3 — Incendio agrícola'),
    ('10-2-4', '10-2-4 — Incendio de microbasural'),
    ('10-2-6', '10-2-6 — Vertedero'),
    ('10-3', '10-3 — Rescate de persona'),
    ('10-4', '10-4 — Rescate vehicular'),
    ('10-4-1', '10-4-1 — Rescate vehicular de vehículo menor'),
    ('10-4-2', '10-4-2 — Rescate de vehículo de carga, maquinaria o transporte'),
    ('10-4-3', '10-4-3 — Rescate vehicular en desnivel, aguas o quebradas'),
    ('10-4-4', '10-4-4 — Rescate vehicular de vehículos de emergencia'),
    ('10-4-5', '10-4-5 — Rescate vehicular relacionado con Hazmat'),
    ('10-5-1', '10-5-1 — Derrame de hidrocarburos'),
    ('10-5-2', '10-5-2 — Incidente con materiales peligrosos'),
    ('10-5-3', '10-5-3 — Atentado con elementos químicos, biológicos o radiológicos'),
    ('10-6-1', '10-6-1 — Emanación de gas combustible'),
    ('10-6-2', '10-6-2 — Explosión de gas'),
    ('10-6-3', '10-6-3 — Explosión de gas con fuego'),
    ('10-6', '10-6 — Emanación de gas'),
    ('10-7', '10-7 — Riesgo eléctrico'),
    ('10-7-1', '10-7-1 — Eléctrico habitacional, comercial o industrial'),
    ('10-7-2', '10-7-2 — Eléctrico en cámara, transformador o subestación'),
    ('10-8', '10-8 — Llamado no clasificado'),
    ('10-8-8', '10-8-8 — Rastreo de persona'),
    ('10-8-10', '10-8-10 — Rastreo en aguas abiertas'),
    ('10-8-11', '10-8-11 — Recuperación de cadáver'),
    ('10-8-12', '10-8-12 — Instrucción, asesorías o capacitación'),
    ('10-8-13', '10-8-13 — Caída de árbol'),
    ('10-8-14', '10-8-14 — Voladuras de techo'),
    ('10-8-15', '10-8-15 — Inundación'),
    ('10-8-16', '10-8-16 — Rescate de animal'),
    ('10-8-18', '10-8-18 — Derrame'),
    ('10-9-1', '10-9-1 — Peritaje solicitado por el Ministerio Público'),
    ('10-9-2', '10-9-2 — Revisión de edificios'),
    ('10-9-3', '10-9-3 — Inspección de local comercial'),
    ('10-9-4', '10-9-4 — Inspección de industrias'),
    ('10-9-5', '10-9-5 — Inspección de grifo'),
    ('10-9-6', '10-9-6 — Simulacros o ejercicios a terceros'),
    ('10-9-7', '10-9-7 — Inspección'),
    ('10-9-19', '10-9-19 — Instrucción, asesorías o capacitación'),
    ('10-10-1', '10-10-1 — Rebrote estructural'),
    ('10-10-2', '10-10-2 — Rebrote forestal'),
    ('10-10', '10-10 — Rebrote de fuego'),
    ('10-11', '10-11 — Servicio o accidente aéreo'),
    ('10-12', '10-12 — Apoyo a otros Cuerpos'),
    ('10-13', '10-13 — Artefacto explosivo o acto terrorista'),
    ('10-14', '10-14 — Accidente de aviación'),
    ('9-3', '9-3 — Acuartelamiento general (histórico)'),
    ('9-4', '9-4 — Acuartelamiento preventivo (histórico)'),
    ('10-1', 'Código histórico 10-1 — Incendio forestal'),
    ('10-2', 'Código histórico 10-2 — Rescate vehicular'),
    ('otro', 'Otro — Tipo de emergencia especificado'),
    ('Otro', 'Otro'),
]


def poblar_especialidades_y_enlazar_personas(apps, schema_editor):
    Especialidad = apps.get_model('usuarios', 'EspecialidadVoluntario')
    Registro = apps.get_model('usuarios', 'RegistroOperativo')
    alias = schema_editor.connection.alias
    for orden, (slug, nombre) in enumerate([
        ('maquinista', 'Maquinista habilitado'),
        ('aspirante_maquinista', 'Aspirante a maquinista'),
        ('rescate', 'Rescate'),
        ('hazmat', 'Hazmat'),
    ], start=1):
        Especialidad.objects.using(alias).get_or_create(
            slug=slug,
            defaults={'nombre': nombre, 'orden': orden, 'activa': True},
        )

    Usuario = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    usuarios = Usuario.objects.using(alias).all().only('id', 'nombre', 'apellido', 'clave_radial')
    por_nombre = {}
    por_clave = {}
    for usuario in usuarios.iterator():
        clave = f'{usuario.nombre} {usuario.apellido}'.strip().casefold()
        por_nombre.setdefault(clave, usuario.pk)
        if usuario.clave_radial:
            por_clave.setdefault(usuario.clave_radial.strip().casefold(), usuario.pk)

    maquinista = Especialidad.objects.using(alias).get(slug='maquinista')
    aspirante = Especialidad.objects.using(alias).get(slug='aspirante_maquinista')
    UsuarioEspecialidades = Usuario.especialidades.through
    for registro in Registro.objects.using(alias).exclude(maquinista_id__isnull=True).only('maquinista_id').distinct().iterator():
        UsuarioEspecialidades.objects.using(alias).get_or_create(
            usuario_id=registro.maquinista_id, especialidadvoluntario_id=maquinista.pk,
        )

    for registro in Registro.objects.using(alias).all().only(
        'id', 'obac', 'aspirante_nombre', 'aspirante_clave',
        'obac_voluntario_id', 'aspirante_voluntario_id'
    ).iterator():
        cambios = []
        if not registro.obac_voluntario_id and registro.obac:
            obac_id = por_nombre.get(registro.obac.strip().casefold())
            if obac_id:
                registro.obac_voluntario_id = obac_id
                cambios.append('obac_voluntario')
        if not registro.aspirante_voluntario_id and registro.aspirante_nombre:
            aspirante_id = (
                por_nombre.get(registro.aspirante_nombre.strip().casefold())
                or por_clave.get((registro.aspirante_clave or '').strip().casefold())
            )
            if aspirante_id:
                registro.aspirante_voluntario_id = aspirante_id
                cambios.append('aspirante_voluntario')
                UsuarioEspecialidades.objects.using(alias).get_or_create(
                    usuario_id=aspirante_id, especialidadvoluntario_id=aspirante.pk,
                )
        if cambios:
            registro.save(using=alias, update_fields=cambios)


def conservar_descripciones_historicas(apps, schema_editor):
    Emergencia = apps.get_model('usuarios', 'Emergencia')
    alias = schema_editor.connection.alias
    opciones_anteriores = dict(Emergencia._meta.get_field('tipo').choices)
    for emergencia in Emergencia.objects.using(alias).all().only('id', 'tipo').iterator():
        etiqueta = opciones_anteriores.get(emergencia.tipo, emergencia.tipo)
        Emergencia.objects.using(alias).filter(pk=emergencia.pk).update(tipo_historico=etiqueta)


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0066_registro_operativo_multiple_unidades'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EspecialidadVoluntario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=50, unique=True)),
                ('nombre', models.CharField(max_length=100, unique=True)),
                ('activa', models.BooleanField(default=True)),
                ('orden', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Especialidad de voluntario',
                'verbose_name_plural': 'Especialidades de voluntarios',
                'ordering': ['orden', 'nombre'],
            },
        ),
        migrations.AddField(
            model_name='usuario',
            name='especialidades',
            field=models.ManyToManyField(blank=True, related_name='voluntarios', to='usuarios.especialidadvoluntario', verbose_name='Especialidades operativas'),
        ),
        migrations.AddField(
            model_name='registrooperativo',
            name='obac_voluntario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registros_operativos_obac', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='registrooperativo',
            name='aspirante_voluntario',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registros_operativos_como_aspirante', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='registrooperativo',
            name='autorizado_por',
            field=models.ManyToManyField(blank=True, related_name='registros_operativos_autorizados', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='emergencia',
            name='tipo_historico',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.RunPython(conservar_descripciones_historicas, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='registrooperativo',
            name='tipo',
            field=models.CharField(choices=TIPOS, max_length=32),
        ),
        migrations.AlterField(
            model_name='emergencia',
            name='tipo',
            field=models.CharField(choices=EMERGENCIA_CHOICES, default='Otro', max_length=50),
        ),
        migrations.RunPython(poblar_especialidades_y_enlazar_personas, migrations.RunPython.noop),
    ]
