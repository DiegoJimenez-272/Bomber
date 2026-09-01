import codecs
import re

with codecs.open('templates/usuarios/emergencias.html', 'r', 'utf-8') as f:
    c = f.read()

c = c.replace('<button type="submit" class="btn btn-danger">Registrar</button>',
'''<div>
                        <button type="submit" name="guardar_incompleto" class="btn btn-warning">Guardar sin completar</button>
                        <button type="submit" name="guardar_completo" class="btn btn-danger">Finalizar Registro</button>
                    </div>''')

c = c.replace('<button type="submit" class="btn btn-danger">Guardar Cambios</button>',
'''<div>
                        <button type="submit" name="guardar_incompleto" class="btn btn-warning">Guardar sin completar</button>
                        <button type="submit" name="guardar_completo" class="btn btn-danger">Finalizar Registro</button>
                    </div>''')

# Document Create
c = re.sub(
    r'(<div class="col-12">\s*<label class="form-label">Personal Asistente</label>[\s\S]*?</div>\s*</div>)',
    r'\1\n                        <div class="col-12">\n                            <label for="{{ form.documento_adjunto.id_for_label }}" class="form-label">Documento Adjunto (Opcional)</label>\n                            {{ form.documento_adjunto }}\n                        </div>',
    c, count=1
)

# Document Edit (the second match)
c = re.sub(
    r'(<div class="col-12">\s*<label class="form-label">Personal Asistente</label>[\s\S]*?</div>\s*</div>)',
    r'\1\n                        <div class="col-12">\n                            <label class="form-label">Documento Adjunto (Dejar en blanco para mantener actual)</label>\n                            <input type="file" name="documento_adjunto" class="form-control">\n                        </div>',
    c
)
# Note: re.sub replaces ALL matches if count isn't specified, but the first one was already replaced above so it doesn't match the same pattern! Wait, the first one WILL NOT match anymore if it got the new block injected after it. But it might match the whole block again. No, `[\s\S]*?` is non-greedy.
# Let's fix this up. We will run it and see.

c = re.sub(
    r'({% elif em.estado == \'Controlada\' %}\s*<span class="badge bg-warning text-dark">Controlada</span>\s*{% else %}\s*<span class="badge bg-secondary">Finalizada</span>\s*{% endif %})',
    r'\1\n                                    {% if not em.registro_completado %}\n                                        <span class="badge bg-warning text-dark ms-1" title="El registro aún no se ha completado">Incompleto</span>\n                                    {% endif %}',
    c
)

c = re.sub(
    r'({% if request.user.is_superuser or request.user.rol.editar_emergencias %}\s*<button class="btn btn-sm btn-outline-primary" data-bs-toggle="modal")',
    r'{% if em.documento_adjunto %}\n                                        <a href="{{ em.documento_adjunto.url }}" target="_blank" class="btn btn-sm btn-outline-secondary me-1" title="Descargar Adjunto"><i class="bi bi-paperclip"></i></a>\n                                    {% endif %}\n                                    \1',
    c
)

with codecs.open('templates/usuarios/emergencias.html', 'w', 'utf-8') as f:
    f.write(c)
