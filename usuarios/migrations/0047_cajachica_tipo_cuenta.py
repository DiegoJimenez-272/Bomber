from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0046_cajachica_origen_egreso"),
    ]

    operations = [
        migrations.RenameField(
            model_name="cajachica",
            old_name="origen_egreso",
            new_name="tipo_cuenta",
        ),
        migrations.AlterField(
            model_name="cajachica",
            name="tipo_cuenta",
            field=models.CharField(
                blank=True,
                choices=[("caja_propia", "Caja propia"), ("cuenta_bancaria", "Cuenta bancaria")],
                default="",
                max_length=20,
                verbose_name="Tipo de cuenta",
            ),
        ),
    ]
