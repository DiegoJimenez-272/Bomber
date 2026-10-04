from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0037_alter_usuario_rut'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehiculo',
            name='estado',
            field=models.CharField(
                choices=[('Disponible', 'Disponible'), ('En Servicio', 'En Servicio'), ('Fuera de Servicio', 'Fuera de Servicio')],
                default='Disponible',
                max_length=20,
            ),
        ),
    ]
