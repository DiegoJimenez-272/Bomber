from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0041_emergenciaunidad_asistentes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salidaterreno',
            name='kilometraje_salida',
            field=models.PositiveIntegerField(verbose_name='Kilometraje de Salida'),
        ),
        migrations.AlterField(
            model_name='salidaterreno',
            name='kilometraje_regreso',
            field=models.PositiveIntegerField(null=True, verbose_name='Kilometraje de Regreso'),
        ),
    ]
