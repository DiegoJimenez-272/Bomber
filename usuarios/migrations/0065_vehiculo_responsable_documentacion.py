from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0064_novedades_licenciamedica'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='vehiculo',
            name='responsable_documentacion',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='vehiculos_responsable_documentacion',
                to=settings.AUTH_USER_MODEL,
                verbose_name='Responsable de documentación',
            ),
        ),
    ]
