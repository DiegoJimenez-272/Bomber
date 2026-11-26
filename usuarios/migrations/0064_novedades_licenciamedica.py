from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0063_registro_operativo'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='rol',
            name='ver_novedades',
            field=models.BooleanField(default=False, verbose_name='Novedades'),
        ),
        migrations.AddField(
            model_name='rol',
            name='editar_novedades',
            field=models.BooleanField(default=False, verbose_name='Editar Novedades'),
        ),
        migrations.CreateModel(
            name='LicenciaMedica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateField(verbose_name='Fecha de inicio')),
                ('fecha_termino', models.DateField(verbose_name='Fecha de término')),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('compania', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='licencias_medicas', to='usuarios.compania')),
                ('integrante', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='licencias_medicas', to=settings.AUTH_USER_MODEL)),
                ('registrado_por', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='licencias_medicas_registradas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Licencia médica',
                'verbose_name_plural': 'Licencias médicas',
                'ordering': ['fecha_termino', 'integrante__apellido', 'integrante__nombre'],
            },
        ),
    ]
