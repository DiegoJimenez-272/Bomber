from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0045_documentos_vehiculo"),
    ]

    operations = [
        migrations.AddField(
            model_name="cajachica",
            name="origen_egreso",
            field=models.CharField(
                blank=True,
                choices=[("caja_propia", "Caja propia"), ("cuenta_bancaria", "Cuenta bancaria")],
                default="",
                max_length=20,
                verbose_name="Origen del egreso",
            ),
        ),
    ]
