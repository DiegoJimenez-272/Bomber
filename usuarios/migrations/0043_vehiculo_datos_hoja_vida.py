from django.db import migrations, models


def limpiar_patentes_nulas(apps, schema_editor):
    Vehiculo = apps.get_model('usuarios', 'Vehiculo')
    Vehiculo.objects.filter(patente__isnull=True).update(patente='')


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0042_obligatorio_kilometraje_salida_terreno'),
    ]

    operations = [
        migrations.RunPython(limpiar_patentes_nulas, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='vehiculo',
            name='patente',
            field=models.CharField(max_length=15, verbose_name='Patente'),
        ),
        migrations.AddField(
            model_name='vehiculo',
            name='marca',
            field=models.CharField(default='', max_length=80, verbose_name='Marca'),
        ),
        migrations.AddField(
            model_name='vehiculo',
            name='modelo',
            field=models.CharField(default='', max_length=80, verbose_name='Modelo'),
        ),
        migrations.AddField(
            model_name='vehiculo',
            name='anio_fabricacion',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Año de fabricación'),
        ),
        migrations.AddField(
            model_name='vehiculo',
            name='anio_puesta_servicio',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Año de puesta en servicio'),
        ),
        migrations.AlterField(
            model_name='vehiculo',
            name='estado',
            field=models.CharField(
                choices=[('Disponible', 'Operativo'), ('En Servicio', 'En Servicio'), ('En Taller', 'En Taller'), ('Fuera de Servicio', 'Fuera de Servicio')],
                default='Disponible',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='vehiculo', name='combustible',
            field=models.CharField(blank=True, choices=[('Diesel', 'Diésel'), ('Gasolina', 'Gasolina'), ('Otro', 'Otro')], default='', max_length=20),
        ),
        migrations.AddField(
            model_name='vehiculo', name='capacidad_estanque_litros',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='vehiculo', name='capacidad_estanque_agua_litros',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='vehiculo', name='capacidad_bomba',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='vehiculo', name='capacidad_bomba_unidad',
            field=models.CharField(blank=True, choices=[('LPM', 'L/min'), ('GPM', 'GPM')], default='', max_length=4),
        ),
        migrations.AddField(
            model_name='vehiculo', name='horometro',
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='vehiculo', name='revision_tecnica_vencimiento',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehiculo', name='permiso_circulacion_vencimiento',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehiculo', name='soap_vencimiento',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehiculo', name='seguro_numero_poliza',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AddField(
            model_name='vehiculo', name='seguro_vencimiento',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehiculo', name='neumaticos_estado',
            field=models.CharField(blank=True, default='', max_length=160),
        ),
        migrations.AddField(
            model_name='vehiculo', name='neumaticos_ultimo_cambio',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='vehiculo', name='bateria_fecha_instalacion',
            field=models.DateField(blank=True, null=True),
        ),
    ]
