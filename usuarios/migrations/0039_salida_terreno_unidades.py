from django.db import migrations, models


def vincular_unidades_existentes(apps, schema_editor):
    SalidaTerreno = apps.get_model('usuarios', 'SalidaTerreno')
    Vehiculo = apps.get_model('usuarios', 'Vehiculo')
    unidades_por_nombre = {}

    for unidad in Vehiculo.objects.all().only('id', 'nombre'):
        clave = unidad.nombre.strip().casefold()
        unidades_por_nombre.setdefault(clave, []).append(unidad.id)

    for salida in SalidaTerreno.objects.all().only('id', 'unidades_involucradas').iterator():
        nombres = (salida.unidades_involucradas or '').replace(';', ',').split(',')
        for nombre in nombres:
            ids = unidades_por_nombre.get(nombre.strip().casefold(), [])
            # Solo vincular nombres únicos para evitar asignar un carro de otra compañía.
            if len(ids) == 1:
                salida.unidades.add(ids[0])


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0038_vehiculo_estado'),
    ]

    operations = [
        migrations.AddField(
            model_name='salidaterreno',
            name='unidades',
            field=models.ManyToManyField(
                blank=True,
                related_name='salidas_terreno',
                to='usuarios.vehiculo',
                verbose_name='Unidades involucradas',
            ),
        ),
        migrations.RunPython(vincular_unidades_existentes, migrations.RunPython.noop),
    ]
