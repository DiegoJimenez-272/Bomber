import codecs

with codecs.open('templates/usuarios/emergencias.html', 'r', 'utf-8') as f:
    c = f.read()

# 1. Highlight the row
c = c.replace('                        <tr>\n                            <td>\n                                <strong>{{ emergencia.get_tipo_display }}</strong>',
'''                        <tr {% if not emergencia.registro_completado %}class="table-warning"{% endif %}>
                            <td>
                                <strong>{{ emergencia.get_tipo_display }}</strong>''')

# 2. Add badge under the state
c = c.replace('''                                {% endif %}
                            </td>
                            <td>''',
'''                                {% endif %}
                                {% if not emergencia.registro_completado %}
                                    <br>
                                    <span class="badge bg-warning text-dark border border-dark mt-1 shadow-sm">
                                        <i class="bi bi-exclamation-triangle-fill me-1"></i>Incompleto
                                    </span>
                                {% endif %}
                            </td>
                            <td>''')

# 3. Add paperclip icon for attachment
c = c.replace('''                            <td>
                                {% if request.user.is_superuser or request.user.rol.editar_emergencias %}
                                <div class="btn-group" role="group">''',
'''                            <td>
                                {% if emergencia.documento_adjunto %}
                                    <a href="{{ emergencia.documento_adjunto.url }}" target="_blank" class="btn btn-sm btn-outline-secondary me-1" title="Descargar Documento Adjunto">
                                        <i class="bi bi-paperclip"></i>
                                    </a>
                                {% endif %}
                                {% if request.user.is_superuser or request.user.rol.editar_emergencias %}
                                <div class="btn-group" role="group">''')

with codecs.open('templates/usuarios/emergencias.html', 'w', 'utf-8') as f:
    f.write(c)

