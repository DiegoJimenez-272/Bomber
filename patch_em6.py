import codecs

with codecs.open('templates/usuarios/emergencias.html', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = list(lines)
        
for i, line in enumerate(new_lines):
    if 'badge bg-secondary' in line and 'Finalizada' in line:
        for j in range(i, i+5):
            if '{% endif %}' in new_lines[j] and 'Incompleto' not in new_lines[j] and 'Incompleto' not in ''.join(new_lines[j:j+2]):
                new_lines[j] = new_lines[j].replace('{% endif %}', '{% endif %}\n                                    {% if not em.registro_completado %}\n                                        <span class="badge bg-warning text-dark ms-1" title="El registro aún no se ha completado"><i class="bi bi-clock-history me-1"></i>Incompleto</span>\n                                    {% endif %}')
                break
                
    if 'data-bs-target="#editEmergenciaModal"' in line and 'btn-outline-primary' in line and 'paperclip' not in ''.join(new_lines[i-2:i+1]):
        new_lines[i] = '                                    {% if em.documento_adjunto %}\n                                        <a href="{{ em.documento_adjunto.url }}" target="_blank" class="btn btn-sm btn-outline-secondary me-1" title="Descargar Documento"><i class="bi bi-paperclip"></i></a>\n                                    {% endif %}\n' + line

with codecs.open('templates/usuarios/emergencias.html', 'w', 'utf-8') as f:
    f.writelines(new_lines)
