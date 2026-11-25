from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0060_rol_estadisticas_operativas'),
    ]

    operations = [
        migrations.AddField(
            model_name='carpeta',
            name='padre',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='subcarpetas',
                to='usuarios.carpeta',
            ),
        ),
        migrations.AddField(
            model_name='documento',
            name='vigente',
            field=models.BooleanField(default=True, verbose_name='Documento vigente'),
        ),
    ]
