from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0057_cajachica_fecha_editable'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CuotaVoluntario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('anio', models.PositiveSmallIntegerField()),
                ('mes', models.PositiveSmallIntegerField()),
                ('creado_en', models.DateTimeField(auto_now_add=True)),
                ('compania', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cuotas_voluntarios', to='usuarios.compania')),
                ('movimiento', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='cuota_voluntario', to='usuarios.cajachica')),
                ('voluntario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cuotas_voluntario', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['voluntario__nombre', 'voluntario__apellido', 'mes'],
            },
        ),
        migrations.AddConstraint(
            model_name='cuotavoluntario',
            constraint=models.UniqueConstraint(fields=('voluntario', 'anio', 'mes'), name='unique_cuota_voluntario_mes'),
        ),
        migrations.AddConstraint(
            model_name='cuotavoluntario',
            constraint=models.CheckConstraint(condition=models.Q(('mes__gte', 1), ('mes__lte', 12)), name='cuota_voluntario_mes_1_12'),
        ),
    ]
