import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0039_salida_terreno_unidades'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SalidaTerrenoUnidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asistentes', models.ManyToManyField(blank=True, related_name='asistencias_salidas_terreno', to=settings.AUTH_USER_MODEL)),
                ('salida', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asistencias_unidades', to='usuarios.salidaterreno')),
                ('unidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asistencias_salidas', to='usuarios.vehiculo')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('salida', 'unidad'), name='unique_unidad_por_salida_terreno')],
            },
        ),
    ]
