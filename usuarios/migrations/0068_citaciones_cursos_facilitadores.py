from django.db import migrations, models
import django.db.models.deletion


CLAVES_CITACION_CURSO = [(f'10-{numero}', f'10-{numero}') for numero in range(20, 31)]


def registrar_referencias_existentes(apps, schema_editor):
    Capacitacion = apps.get_model('usuarios', 'Capacitacion')
    Facilitador = apps.get_model('usuarios', 'FacilitadorCapacitacion')
    alias = schema_editor.connection.alias
    nombres = Capacitacion.objects.using(alias).exclude(instructor='').exclude(
        instructor='No especificado'
    ).values_list('instructor', flat=True).distinct()
    for nombre in nombres.iterator(chunk_size=500):
        nombre = nombre.strip()
        if not nombre:
            continue
        facilitador, _ = Facilitador.objects.using(alias).get_or_create(
            nombre=nombre,
            defaults={'tipo': 'sin_clasificar', 'activo': True},
        )
        Capacitacion.objects.using(alias).filter(
            instructor=nombre, facilitador_id__isnull=True,
        ).update(facilitador_id=facilitador.pk)


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0067_registro_operativo_catalogos'),
    ]

    operations = [
        migrations.CreateModel(
            name='FacilitadorCapacitacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=150, unique=True)),
                ('tipo', models.CharField(choices=[('instructor', 'Instructor'), ('entidad_externa', 'Entidad externa'), ('sin_clasificar', 'Referencia histórica por clasificar')], default='instructor', max_length=24)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Instructor o entidad externa',
                'verbose_name_plural': 'Instructores y entidades externas',
                'ordering': ['tipo', 'nombre'],
            },
        ),
        migrations.AddField(
            model_name='capacitacion',
            name='clave_citacion_curso',
            field=models.CharField(blank=True, choices=CLAVES_CITACION_CURSO, default='', max_length=5, verbose_name='Citación o curso'),
        ),
        migrations.AddField(
            model_name='capacitacion',
            name='curso_malla',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='capacitaciones_registradas', to='usuarios.cursomalla', verbose_name='Curso oficial de la Malla Curricular'),
        ),
        migrations.AddField(
            model_name='capacitacion',
            name='facilitador',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='capacitaciones', to='usuarios.facilitadorcapacitacion', verbose_name='Instructor o entidad externa'),
        ),
        migrations.AlterField(
            model_name='capacitacion',
            name='malla',
            field=models.CharField(choices=[('Nivel postulante', 'Nivel postulante'), ('Nivel inicial', 'Nivel inicial'), ('Nivel operativo', 'Nivel operativo'), ('Nivel profesional', 'Nivel profesional'), ('Nivel especialidad', 'Nivel especialidad'), ('Cursos complementarios', 'Cursos complementarios'), ('Otros', 'Otros')], default='Otros', max_length=50, verbose_name='Malla/Curso'),
        ),
        migrations.RunPython(registrar_referencias_existentes, migrations.RunPython.noop),
    ]
