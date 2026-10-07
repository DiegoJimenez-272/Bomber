import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0040_salidaterrenounidad_asistentes'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmergenciaUnidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asistentes', models.ManyToManyField(blank=True, related_name='asistencias_emergencias_unidad', to=settings.AUTH_USER_MODEL)),
                ('emergencia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unidades_asistencia', to='usuarios.emergencia')),
                ('unidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asistencias_emergencias', to='usuarios.vehiculo')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('emergencia', 'unidad'), name='unique_unidad_por_emergencia')],
            },
        ),
    ]
