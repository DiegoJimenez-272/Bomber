from django.db import migrations


def agregar_guia_emergencias(apps, schema_editor):
    GuiaChatbot = apps.get_model('usuarios', 'GuiaChatbot')
    GuiaChatbot.objects.get_or_create(
        titulo='Consultar emergencias',
        defaults={
            'palabras_clave': 'emergencia, emergencias, consultar emergencia, ver emergencia, listado de emergencias',
            'pasos': 'Abre Emergencias desde el menú lateral para revisar los registros y usar los filtros disponibles.',
            'modulo': 'emergencias',
            'prioridad': 0,
            'activo': True,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0053_chatbot_reglas'),
    ]

    operations = [
        migrations.RunPython(agregar_guia_emergencias, migrations.RunPython.noop),
    ]
