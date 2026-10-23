import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0051_rol_malla_curricular_permissions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ReporteError',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=120, verbose_name='Nombre del error')),
                ('descripcion', models.TextField(max_length=5000, verbose_name='Descripción del error')),
                ('reportante_nombre', models.CharField(max_length=200, verbose_name='Nombre del reportante')),
                ('reportante_compania', models.CharField(blank=True, default='', max_length=80, verbose_name='Compañía del reportante')),
                ('reportante_rol', models.CharField(blank=True, default='', max_length=80, verbose_name='Rol del reportante')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('estado', models.CharField(choices=[('pendiente', 'En espera'), ('corregido', 'Corregido')], db_index=True, default='pendiente', max_length=20)),
                ('fecha_resolucion', models.DateTimeField(blank=True, null=True)),
                ('corregido_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reportes_errores_corregidos', to=settings.AUTH_USER_MODEL)),
                ('creado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reportes_errores_creados', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Reporte de error',
                'verbose_name_plural': 'Reportes de errores',
                'ordering': ['-fecha_creacion'],
            },
        ),
    ]
