from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def copiar_unidades_existentes(apps, schema_editor):
    RegistroOperativo = apps.get_model('usuarios', 'RegistroOperativo')
    RegistroOperativoUnidad = apps.get_model('usuarios', 'RegistroOperativoUnidad')
    alias = schema_editor.connection.alias
    registros = RegistroOperativo.objects.using(alias).exclude(vehiculo_id__isnull=True).prefetch_related('asistentes')
    for registro in registros.iterator():
        detalle = RegistroOperativoUnidad.objects.using(alias).create(
            registro_id=registro.pk,
            unidad_id=registro.vehiculo_id,
        )
        detalle.asistentes.set(registro.asistentes.using(alias).values_list('pk', flat=True))


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0065_vehiculo_responsable_documentacion'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistroOperativoUnidad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asistentes', models.ManyToManyField(blank=True, related_name='asistencias_por_unidad_operativa', to=settings.AUTH_USER_MODEL)),
                ('registro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unidades_asignadas', to='usuarios.registrooperativo')),
                ('unidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='detalles_registros_operativos', to='usuarios.vehiculo')),
            ],
            options={
                'ordering': ['unidad__nombre'],
            },
        ),
        migrations.AddField(
            model_name='registrooperativo',
            name='unidades',
            field=models.ManyToManyField(blank=True, related_name='registros_operativos_asignados', through='usuarios.RegistroOperativoUnidad', to='usuarios.vehiculo'),
        ),
        migrations.RunPython(copiar_unidades_existentes, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='registrooperativounidad',
            constraint=models.UniqueConstraint(fields=('registro', 'unidad'), name='unique_unidad_por_registro_operativo'),
        ),
    ]
