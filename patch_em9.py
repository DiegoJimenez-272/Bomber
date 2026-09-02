import codecs

with codecs.open('templates/usuarios/emergencias.html', 'r', 'utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '<tr>' in line and lines[i+1].strip() == '<td>' and '<strong>{{ emergencia.get_tipo_display }}</strong>' in lines[i+2]:
        lines[i] = '                        <tr {% if not emergencia.registro_completado %}class="table-warning"{% endif %}>\n'

    if '{% endif %}' in line and lines[i+1].strip() == '</td>' and lines[i+2].strip() == '<td>' and '{% if request.user.is_superuser or request.user.rol.editar_emergencias %}' in lines[i+3]:
        lines[i] = '                                {% endif %}\n                                {% if not emergencia.registro_completado %}\n                                    <br>\n                                    <span class="badge bg-warning text-dark border border-dark mt-1 shadow-sm">\n                                        <i class="bi bi-exclamation-triangle-fill me-1"></i>Incompleto\n                                    </span>\n                                {% endif %}\n'

    if '<td>' in line and '{% if request.user.is_superuser or request.user.rol.editar_emergencias %}' in lines[i+1]:
        # Add the document link
        lines[i] = '                            <td>\n                                {% if emergencia.documento_adjunto %}\n                                    <a href="{{ emergencia.documento_adjunto.url }}" target="_blank" class="btn btn-sm btn-outline-secondary me-1" title="Descargar Adjunto"><i class="bi bi-paperclip"></i></a>\n                                {% endif %}\n'

with codecs.open('templates/usuarios/emergencias.html', 'w', 'utf-8') as f:
    f.writelines(lines)
