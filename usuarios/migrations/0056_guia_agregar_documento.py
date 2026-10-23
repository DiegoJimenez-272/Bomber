from django.db import migrations


def agregar_guia_documentos(apps, schema_editor):
    GuiaChatbot = apps.get_model('usuarios', 'GuiaChatbot')
    GuiaChatbot.objects.get_or_create(
        titulo='Agregar un documento al sistema',
        defaults={
            'palabras_clave': 'agregar documento, agrego documento, agregar un documento, añadir documento, anadir documento, cargar documento, subir documento, adjuntar documento, adjuntar archivo',
            'pasos': '1. Abre Documentos.\n2. Pulsa “Subir Documento”.\n3. Escribe el nombre, selecciona la clasificación y el archivo.\n4. Si quieres, elige una carpeta y marca si será privado.\n5. Pulsa “Subir”.\nPara redactarlo dentro del sistema y generar un PDF, usa “Redactar Documento”. Necesitas permiso para editar Documentos.',
            'modulo': 'documentos',
            'prioridad': 11,
            'activo': True,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0055_guias_procedimientos_erp'),
    ]

    operations = [
        migrations.RunPython(agregar_guia_documentos, migrations.RunPython.noop),
    ]
