from django.db import migrations, models


def renombrar_taller_a_ejercicio(apps, schema_editor):
    Capacitacion = apps.get_model('usuarios', 'Capacitacion')
    Capacitacion.objects.filter(tipo_actividad='Taller').update(
        tipo_actividad='Ejercicio de compañía'
    )


def restaurar_ejercicio_a_taller(apps, schema_editor):
    Capacitacion = apps.get_model('usuarios', 'Capacitacion')
    Capacitacion.objects.filter(tipo_actividad='Ejercicio de compañía').update(
        tipo_actividad='Taller'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0058_cuota_voluntario'),
    ]

    operations = [
        migrations.RunPython(
            renombrar_taller_a_ejercicio,
            restaurar_ejercicio_a_taller,
        ),
        migrations.AlterField(
            model_name='capacitacion',
            name='tipo_actividad',
            field=models.CharField(
                choices=[
                    ('Curso', 'Curso'),
                    ('Reunión', 'Reunión'),
                    ('Ejercicio de compañía', 'Ejercicio de compañía'),
                    ('Campaña económica', 'Campaña económica'),
                    ('Charla', 'Charla'),
                    ('Visita', 'Visita'),
                    ('Otro', 'Otro'),
                ],
                default='Curso',
                max_length=50,
                verbose_name='Tipo de Actividad',
            ),
        ),
    ]
