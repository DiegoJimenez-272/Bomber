from django.db import migrations, models


def conservar_acceso_actual(apps, schema_editor):
    Rol = apps.get_model('usuarios', 'Rol')
    Rol.objects.filter(
        models.Q(ver_resumen_general=True)
        | models.Q(ver_emergencias=True)
        | models.Q(ver_salidas_terreno=True)
        | models.Q(ver_mantenimientos=True)
        | models.Q(ver_inventario=True)
    ).update(ver_estadisticas_operativas=True)


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0059_actualizar_tipos_actividad'),
    ]

    operations = [
        migrations.AddField(
            model_name='rol',
            name='ver_estadisticas_operativas',
            field=models.BooleanField(default=False, verbose_name='Estadísticas Operativas'),
        ),
        migrations.RunPython(conservar_acceso_actual, migrations.RunPython.noop),
    ]
