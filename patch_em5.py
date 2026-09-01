import codecs

with codecs.open('templates/usuarios/emergencias.html', 'r', 'utf-8') as f:
    c = f.read()

# Add badge
badge_target = "{% endif %}"
badge_insertion = """{% endif %}
                                    {% if not em.registro_completado %}
                                        <span class="badge bg-warning text-dark ms-1" title="El registro aún no se ha completado">Incompleto</span>
                                    {% endif %}"""

# Need to find the exact line
# It looks like:
#                                     {% else %}
#                                         <span class="badge bg-secondary">Finalizada</span>
#                                     {% endif %}

badge_find = '''                                    {% else %}
                                        <span class="badge bg-secondary">Finalizada</span>
                                    {% endif %}'''
badge_replace = '''                                    {% else %}
                                        <span class="badge bg-secondary">Finalizada</span>
                                    {% endif %}
                                    {% if not em.registro_completado %}
                                        <span class="badge bg-warning text-dark ms-1" title="El registro aún no se ha completado"><i class="bi bi-clock-history me-1"></i>Incompleto</span>
                                    {% endif %}'''
c = c.replace(badge_find, badge_replace)

# Add attachment icon
actions_find = '''                                    {% if request.user.is_superuser or request.user.rol.editar_emergencias %}
                                    <button class="btn btn-sm btn-outline-primary" data-bs-toggle="modal"'''

actions_replace = '''                                    {% if em.documento_adjunto %}
                                        <a href="{{ em.documento_adjunto.url }}" target="_blank" class="btn btn-sm btn-outline-secondary me-1" title="Descargar Documento Adjunto"><i class="bi bi-paperclip"></i></a>
                                    {% endif %}
                                    {% if request.user.is_superuser or request.user.rol.editar_emergencias %}
                                    <button class="btn btn-sm btn-outline-primary" data-bs-toggle="modal"'''
c = c.replace(actions_find, actions_replace)

with codecs.open('templates/usuarios/emergencias.html', 'w', 'utf-8') as f:
    f.write(c)
