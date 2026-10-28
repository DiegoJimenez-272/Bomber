from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0056_guia_agregar_documento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cajachica',
            name='fecha',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
