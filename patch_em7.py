import codecs

with codecs.open('templates/usuarios/emergencias.html', 'r', 'utf-8') as f:
    c = f.read()

badge_target = '''                                {% else %}
                                    <span class="badge bg-success">{{ emergencia.estado }}</span>
                                {% endif %}'''
badge_replace = '''                                {% else %}
                                    <span class="badge bg-success">{{ emergencia.estado }}</span>
                                {% endif %}
                                {% if not emergencia.registro_completado %}
                                    <span class="badge bg-warning text-dark mt-1" title="El registro aún no se ha completado"><i class="bi bi-clock-history me-1"></i>Incompleto</span>
                                {% endif %}'''

c = c.replace(badge_target, badge_replace)

actions_target = '''                                {% if request.user.is_superuser or request.user.rol.editar_emergencias %}
                                <div class="btn-group" role="group">'''
actions_replace = '''                                {% if emergencia.documento_adjunto %}
                                    <a href="{{ emergencia.documento_adjunto.url }}" target="_blank" class="btn btn-sm btn-outline-secondary me-1" title="Descargar Adjunto"><i class="bi bi-paperclip"></i></a>
                                {% endif %}
                                {% if request.user.is_superuser or request.user.rol.editar_emergencias %}
                                <div class="btn-group" role="group">'''

c = c.replace(actions_target, actions_replace)

with codecs.open('templates/usuarios/emergencias.html', 'w', 'utf-8') as f:
    f.write(c)
