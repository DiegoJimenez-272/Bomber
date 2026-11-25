from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0062_devolucion_inventario'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='emergencia',
            name='tipo',
            field=models.CharField(choices=[('10-0-1', 'Llamado Estructural'), ('10-0-2', 'Llamado a Vehículo'), ('10-1', 'Incendio Forestal'), ('10-2', 'Rescate Vehicular'), ('10-3', 'Rescate de Personas'), ('10-4', 'Materiales Peligrosos'), ('10-4-1', 'Emergencia vehicular 10-4-1'), ('10-4-2', 'Emergencia vehicular 10-4-2'), ('10-4-3', 'Emergencia vehicular 10-4-3'), ('10-4-4', 'Emergencia vehicular 10-4-4'), ('10-4-5', 'Emergencia vehicular 10-4-5'), ('Otro', 'Otro')], default='Otro', max_length=50),
        ),
        migrations.AddField(
            model_name='vehiculo',
            name='odometro_actual',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Odómetro actual (km)'),
        ),
        migrations.CreateModel(
            name='RegistroOperativo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('emergencia', 'Emergencia'), ('emergencia_vehicular', 'Emergencia vehicular (10-4)'), ('servicio_especial', 'Servicio especial'), ('practica_maquinista', 'Práctica de maquinista'), ('rodaje_6_13', 'Se dirige a (6-13) — Rodaje'), ('combustible_6_14', 'Carga de combustible (6-14)'), ('ronda_maquinistas', 'Ronda de maquinistas'), ('llegada_cuartel', 'Voluntarios llegados al cuartel')], max_length=32)),
                ('codigo', models.CharField(blank=True, default='', max_length=80)),
                ('fecha_inicio', models.DateField()),
                ('fecha_termino', models.DateField(blank=True, null=True)),
                ('hora_despacho', models.TimeField(blank=True, null=True)),
                ('hora_llegada', models.TimeField(blank=True, null=True)),
                ('kilometraje_despacho', models.PositiveIntegerField(blank=True, null=True)),
                ('kilometraje_llegada', models.PositiveIntegerField(blank=True, null=True)),
                ('direccion', models.CharField(blank=True, default='', max_length=255)),
                ('estacion_servicio', models.CharField(blank=True, choices=[('copec', 'Copec'), ('shell', 'Shell'), ('aramco', 'Aramco'), ('otra', 'Otra')], default='', max_length=30)),
                ('estacion_detalle', models.CharField(blank=True, default='', max_length=180)),
                ('obac', models.CharField(blank=True, default='', max_length=160)),
                ('instituciones_apoyo', models.JSONField(blank=True, default=list)),
                ('apoyo_otro_cuerpo', models.CharField(blank=True, default='', max_length=160)),
                ('apoyo_otros', models.CharField(blank=True, default='', max_length=255)),
                ('informe', models.TextField(blank=True, default='')),
                ('novedades_unidad', models.TextField(blank=True, default='')),
                ('lesionados_externos', models.TextField(blank=True, default='')),
                ('involucrados', models.JSONField(blank=True, default=list)),
                ('autorizaciones', models.JSONField(blank=True, default=list)),
                ('aspirante_nombre', models.CharField(blank=True, default='', max_length=160)),
                ('aspirante_clave', models.CharField(blank=True, default='', max_length=40)),
                ('combustible_tipo', models.CharField(blank=True, choices=[('diesel', 'Diésel'), ('bencina_93', 'Bencina 93'), ('bencina_95', 'Bencina 95'), ('bencina_97', 'Bencina 97'), ('otro', 'Otro')], default='', max_length=20)),
                ('monto_combustible', models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
                ('checklist', models.JSONField(blank=True, default=list)),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('asistentes', models.ManyToManyField(blank=True, related_name='asistencias_registros_operativos', to=settings.AUTH_USER_MODEL)),
                ('creado_por', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registros_operativos_creados', to=settings.AUTH_USER_MODEL)),
                ('emergencia', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registros_operativos', to='usuarios.emergencia')),
                ('instructor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='practicas_maquinista_instructor', to=settings.AUTH_USER_MODEL)),
                ('maquinista', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registros_operativos_conduccion', to=settings.AUTH_USER_MODEL)),
                ('movimiento_caja', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registro_operativo', to='usuarios.cajachica')),
                ('salida_terreno', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registros_operativos', to='usuarios.salidaterreno')),
                ('vehiculo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registros_operativos', to='usuarios.vehiculo')),
            ],
            options={
                'verbose_name': 'Registro operativo',
                'verbose_name_plural': 'Registros operativos',
                'ordering': ['-fecha_inicio', '-creado_en'],
            },
        ),
    ]
