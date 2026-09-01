import codecs
import re

with codecs.open('templates/usuarios/emergencias.html', 'r', 'utf-8') as f:
    c = f.read()

# 1. Add enctype and novalidate
c = c.replace('<form method="post">', '<form method="post" enctype="multipart/form-data" novalidate>')
c = c.replace('<form id="editEmergenciaForm" method="post">', '<form id="editEmergenciaForm" method="post" enctype="multipart/form-data" novalidate>')

# 2. Add Documento Adjunto to Create Modal (finding the 'asistentes' block)
target_create_asist = """                        <div class="col-12">
                            <label class="form-label">Personal Asistente</label>
                            <div class="border rounded p-3 bg-light" style="max-height: 200px; overflow-y: auto;">
                                {% for checkbox in form.asistentes %}
                                <div class="form-check">
                                    {{ checkbox.tag }}
                                    <label class="form-check-label" for="{{ checkbox.id_for_label }}">
                                        {{ checkbox.choice_label }}
                                    </label>
                                </div>
                                {% endfor %}
                            </div>
                        </div>"""

replacement_create_asist = target_create_asist + """
                        <div class="col-12">
                            <label for="{{ form.documento_adjunto.id_for_label }}" class="form-label">Documento Adjunto (Opcional)</label>
                            {{ form.documento_adjunto }}
                        </div>"""

c = c.replace(target_create_asist, replacement_create_asist)

# 3. Add Documento Adjunto to Edit Modal
target_edit_asist = """                        <div class="col-12">
                            <label class="form-label">Personal Asistente</label>
                            <div class="border rounded p-3 bg-light" style="max-height: 200px; overflow-y: auto;">
                                {% for checkbox in form.asistentes %}
                                <div class="form-check">
                                    <input type="checkbox" name="asistentes" value="{{ checkbox.data.value }}" class="form-check-input" id="edit_asistente_{{ checkbox.data.value }}">
                                    <label class="form-check-label" for="edit_asistente_{{ checkbox.data.value }}">
                                        {{ checkbox.choice_label }}
                                    </label>
                                </div>
                                {% endfor %}
                            </div>
                        </div>"""

replacement_edit_asist = target_edit_asist + """
                        <div class="col-12">
                            <label class="form-label">Documento Adjunto (Dejar en blanco para mantener actual)</label>
                            <input type="file" name="documento_adjunto" class="form-control">
                        </div>"""

c = c.replace(target_edit_asist, replacement_edit_asist)


# 4. Modify Footer Buttons (Create Modal)
target_create_footer = """                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="submit" class="btn btn-primary">Registrar Emergencia</button>
                </div>"""

replacement_create_footer = """                <div class="modal-footer justify-content-between">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <div>
                        <button type="submit" name="guardar_incompleto" class="btn btn-warning">Guardar sin completar</button>
                        <button type="submit" name="guardar_completo" class="btn btn-primary">Finalizar Registro</button>
                    </div>
                </div>"""

c = c.replace(target_create_footer, replacement_create_footer)

# 5. Modify Footer Buttons (Edit Modal)
target_edit_footer = """                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <button type="submit" class="btn btn-primary">Actualizar Emergencia</button>
                </div>"""

replacement_edit_footer = """                <div class="modal-footer justify-content-between">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                    <div>
                        <button type="submit" name="guardar_incompleto" class="btn btn-warning">Guardar sin completar</button>
                        <button type="submit" name="guardar_completo" class="btn btn-primary">Finalizar Registro</button>
                    </div>
                </div>"""

c = c.replace(target_edit_footer, replacement_edit_footer)


# 6. Show "Incompleto" badge in the table
target_badge = """                                    {% if em.estado == 'Activa' %}
                                        <span class="badge bg-danger">Activa</span>
                                    {% elif em.estado == 'Controlada' %}
                                        <span class="badge bg-warning text-dark">Controlada</span>
                                    {% else %}
                                        <span class="badge bg-secondary">Finalizada</span>
                                    {% endif %}"""

replacement_badge = """                                    {% if em.estado == 'Activa' %}
                                        <span class="badge bg-danger">Activa</span>
                                    {% elif em.estado == 'Controlada' %}
                                        <span class="badge bg-warning text-dark">Controlada</span>
                                    {% else %}
                                        <span class="badge bg-secondary">Finalizada</span>
                                    {% endif %}
                                    {% if not em.registro_completado %}
                                        <span class="badge bg-warning text-dark ms-1" title="El registro aún no se ha completado">Incompleto</span>
                                    {% endif %}"""

c = c.replace(target_badge, replacement_badge)

# 7. Add download link to Documento Adjunto in table (maybe in actions)
target_actions = """                                    {% if request.user.is_superuser or request.user.rol.editar_emergencias %}
                                    <button class="btn btn-sm btn-outline-primary" data-bs-toggle="modal" data-bs-target="#editEmergenciaModal" """

replacement_actions = """                                    {% if em.documento_adjunto %}
                                        <a href="{{ em.documento_adjunto.url }}" target="_blank" class="btn btn-sm btn-outline-secondary" title="Descargar Adjunto"><i class="bi bi-paperclip"></i></a>
                                    {% endif %}
                                    {% if request.user.is_superuser or request.user.rol.editar_emergencias %}
                                    <button class="btn btn-sm btn-outline-primary" data-bs-toggle="modal" data-bs-target="#editEmergenciaModal" """

c = c.replace(target_actions, replacement_actions)

with codecs.open('templates/usuarios/emergencias.html', 'w', 'utf-8') as f:
    f.write(c)

