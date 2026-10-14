from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0050_malla_curricular'),
    ]

    operations = [
        migrations.AddField(
            model_name='rol',
            name='ver_malla_curricular',
            field=models.BooleanField(default=False, verbose_name='Malla Curricular'),
        ),
        migrations.AddField(
            model_name='rol',
            name='editar_malla_curricular',
            field=models.BooleanField(default=False, verbose_name='Editar Malla Curricular'),
        ),
    ]
