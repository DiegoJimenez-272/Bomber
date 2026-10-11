import usuarios.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0044_ronda_vehiculo'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehiculo',
            name='revision_tecnica_archivo',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=usuarios.validators.SecureFilePath('vehiculos_documentacion/'),
                validators=[usuarios.validators.validar_documento_vehiculo],
                verbose_name='Documento de revisión técnica',
            ),
        ),
        migrations.AddField(
            model_name='vehiculo',
            name='permiso_circulacion_archivo',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=usuarios.validators.SecureFilePath('vehiculos_documentacion/'),
                validators=[usuarios.validators.validar_documento_vehiculo],
                verbose_name='Documento de permiso de circulación',
            ),
        ),
    ]
