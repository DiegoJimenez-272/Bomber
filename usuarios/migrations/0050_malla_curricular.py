from django.conf import settings
from django.db import migrations, models


RAMOS = [
    ('Nivel postulante', 1, 'Introducción a la Historia y Funcionamiento de Bomberos de Chile (BORA)', False, True),
    ('Nivel postulante', 2, 'Introducción a Equipos de Protección Personal y Primera Respuesta', False, True),
    ('Nivel inicial', 1, 'Bomberos: Origen y Rol Actual (BORA)', False, False),
    ('Nivel inicial', 2, 'Comunicaciones para Bomberos', False, False),
    ('Nivel inicial', 3, 'Gestión de Riesgos Bomberiles', False, True),
    ('Nivel inicial', 4, 'Comportamiento Humano en Emergencias', False, True),
    ('Nivel inicial', 5, 'Equipos de Protección Personal para Bomberos', False, False),
    ('Nivel inicial', 6, 'Fuego y Tácticas', False, False),
    ('Nivel inicial', 7, 'Reanimación Cardiopulmonar para Bomberos', False, False),
    ('Nivel inicial', 8, 'Control de Incendios Forestales', False, True),
    ('Nivel operativo', 1, 'Ventilación Táctica', False, False),
    ('Nivel operativo', 2, 'Entrada Forzada', False, False),
    ('Nivel operativo', 3, 'Escalas y Cuerdas para el Control de Incendios', False, False),
    ('Nivel operativo', 4, 'Búsqueda y Rescate en Incendios Estructurales', False, False),
    ('Nivel operativo', 5, 'Sobrevivencia en Incendios Estructurales', False, False),
    ('Nivel operativo', 6, 'Riesgos Eléctricos', False, False),
    ('Nivel operativo', 7, 'Soporte Vital Básico (SVB)', False, False),
    ('Nivel operativo', 8, 'Introductorio CRIMAP', False, True),
    ('Nivel operativo', 9, 'Curso Básico Sistema de Comando de Incidentes (2026)', False, False),
    ('Nivel profesional', 1, 'Control de Emergencias con Gases Combustibles', False, False),
    ('Nivel profesional', 2, 'Control de Fuego en Vehículos', False, False),
    ('Nivel profesional', 3, 'Control de Incendios Estructurales', False, False),
    ('Nivel profesional', 4, 'Oficial de Seguridad del Incidente', False, False),
    ('Nivel profesional', 5, 'Mandos Superiores', False, True),
    ('Nivel profesional', 6, 'Curso de Primera Respuesta a Incidentes con Materiales Peligrosos (CRIMAP) (2026)', False, False),
    ('Cursos complementarios', 1, 'Primera Respuesta en Rescate Técnico para No Especialistas', True, True),
    ('Cursos complementarios', 2, 'Promoción de la Cultura de la Equidad', True, True),
    ('Cursos complementarios', 3, 'Lengua de Señas Chilena con Perspectiva de Emergencias', True, True),
]


def crear_ramos_iniciales(apps, schema_editor):
    CursoMalla = apps.get_model('usuarios', 'CursoMalla')
    for nivel, orden, nombre, complementario, aula_virtual in RAMOS:
        CursoMalla.objects.get_or_create(
            nombre=nombre,
            defaults={
                'nivel': nivel,
                'orden': orden,
                'complementario': complementario,
                'aula_virtual': aula_virtual,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0049_rol_gestionar_inventario_todas_companias'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CursoMalla',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=220, unique=True)),
                ('nivel', models.CharField(choices=[('Nivel postulante', 'Nivel postulante'), ('Nivel inicial', 'Nivel inicial'), ('Nivel operativo', 'Nivel operativo'), ('Nivel profesional', 'Nivel profesional'), ('Cursos complementarios', 'Cursos complementarios')], max_length=40)),
                ('orden', models.PositiveSmallIntegerField(default=0)),
                ('complementario', models.BooleanField(default=False)),
                ('aula_virtual', models.BooleanField(default=False)),
                ('usuarios', models.ManyToManyField(blank=True, related_name='ramos_malla_curricular', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Ramo de la malla curricular',
                'verbose_name_plural': 'Ramos de la malla curricular',
                'ordering': ['nivel', 'orden', 'nombre'],
            },
        ),
        migrations.RunPython(crear_ramos_iniciales, migrations.RunPython.noop),
    ]
