from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0043_vehiculo_datos_hoja_vida'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RondaVehiculo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('tipo_hallazgo', models.CharField(choices=[('Sin novedad', 'Sin novedad'), ('Falla', 'Falla'), ('Observación', 'Observación'), ('Otro', 'Otro')], default='Sin novedad', max_length=20)),
                ('detalle', models.TextField(verbose_name='Falla, observación o detalle')),
                ('estado_operativo', models.CharField(blank=True, choices=[('Disponible', 'Operativo'), ('En Servicio', 'En Servicio'), ('En Taller', 'En Taller'), ('Fuera de Servicio', 'Fuera de Servicio')], max_length=20)),
                ('registrado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rondas_vehiculos', to=settings.AUTH_USER_MODEL)),
                ('vehiculo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rondas', to='usuarios.vehiculo')),
            ],
            options={
                'verbose_name': 'Ronda de vehículo',
                'verbose_name_plural': 'Rondas de vehículos',
                'ordering': ['-fecha'],
            },
        ),
    ]
