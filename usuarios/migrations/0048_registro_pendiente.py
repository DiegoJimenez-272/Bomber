import django.utils.timezone
import usuarios.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("usuarios", "0047_cajachica_tipo_cuenta"),
    ]

    operations = [
        migrations.CreateModel(
            name="RegistroPendiente",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("email", models.EmailField(max_length=80, unique=True)),
                ("nombre", models.CharField(max_length=80)),
                ("apellido", models.CharField(max_length=80)),
                ("rut", models.CharField(max_length=15)),
                ("clave_radial", models.CharField(blank=True, max_length=20, null=True)),
                ("foto_perfil", models.ImageField(blank=True, null=True, upload_to=usuarios.validators.SecureFilePath("registros_pendientes/"), validators=[usuarios.validators.validar_extension_imagen])),
                ("password", models.CharField(max_length=128)),
                ("codigo", models.CharField(max_length=6)),
                ("creado_en", models.DateTimeField(default=django.utils.timezone.now)),
                ("intentos", models.PositiveIntegerField(default=0)),
                ("compania", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="usuarios.compania")),
            ],
        ),
    ]
