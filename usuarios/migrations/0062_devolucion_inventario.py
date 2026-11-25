from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import usuarios.validators


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0061_documentos_carpetas_y_vigencia'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DevolucionInventario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('compania_nombre', models.CharField(blank=True, max_length=80)),
                ('nombre_item', models.CharField(max_length=200)),
                ('entregado_a', models.CharField(blank=True, max_length=160)),
                ('ubicacion_anterior', models.CharField(blank=True, max_length=150)),
                ('ubicacion_retorno', models.CharField(max_length=150)),
                ('estado_retorno', models.CharField(choices=[('Bueno', 'Bueno'), ('Regular', 'Regular'), ('Malo', 'Malo'), ('En Reparación', 'En Reparación'), ('De Baja', 'De Baja')], max_length=20)),
                ('observaciones', models.TextField(blank=True)),
                ('acta', models.FileField(blank=True, upload_to=usuarios.validators.SecureFilePath('devoluciones/actas/'), validators=[usuarios.validators.validar_extension_archivo])),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('compania', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='devoluciones_inventario', to='usuarios.compania')),
                ('item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='devoluciones', to='usuarios.inventario')),
                ('realizado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='devoluciones_inventario_registradas', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Devolución de inventario',
                'verbose_name_plural': 'Devoluciones de inventario',
                'ordering': ['-creado_en'],
            },
        ),
        migrations.CreateModel(
            name='DevolucionInventarioFoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.ImageField(upload_to=usuarios.validators.SecureFilePath('devoluciones/fotos/'), validators=[usuarios.validators.validar_extension_imagen])),
                ('devolucion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fotos', to='usuarios.devolucioninventario')),
            ],
        ),
    ]
