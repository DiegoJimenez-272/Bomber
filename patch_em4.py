import codecs

with codecs.open('templates/usuarios/emergencias.html', 'r', 'utf-8') as f:
    c = f.read()

create_input = '''
                <div class="modal-body border-top pt-3">
                    <div class="row">
                        <div class="col-12">
                            <label for="{{ form.documento_adjunto.id_for_label }}" class="form-label">Documento Adjunto (Opcional)</label>
                            {{ form.documento_adjunto }}
                        </div>
                    </div>
                </div>
                <div class="modal-footer justify-content-between">'''

edit_input = '''
                <div class="modal-body border-top pt-3">
                    <div class="row">
                        <div class="col-12">
                            <label class="form-label">Documento Adjunto (Dejar en blanco para mantener actual)</label>
                            <input type="file" name="documento_adjunto" class="form-control">
                        </div>
                    </div>
                </div>
                <div class="modal-footer justify-content-between">'''

parts = c.split('<div class="modal-footer justify-content-between">')
if len(parts) == 4:
    new_c = parts[0] + create_input + parts[1] + edit_input + parts[2] + '<div class="modal-footer justify-content-between">' + parts[3]
    with codecs.open('templates/usuarios/emergencias.html', 'w', 'utf-8') as f:
        f.write(new_c)

