import codecs
import re

with codecs.open('templates/usuarios/perfil.html', 'r', 'utf-8') as f:
    c = f.read()

# Remove the tab button
c = re.sub(r'<li class="nav-item" role="presentation"><button class="btn btn-outline-danger" id="change-password-tab" data-bs-toggle="tab" data-bs-target="#change-password".*?Seguridad</button></li>\n*', '', c)

# Remove the tab pane
c = re.sub(r'<!-- Pestaña Cambiar Contraseña -->\s*<div class="tab-pane fade" id="change-password" role="tabpanel">.*?</div>(?=\s*<!-- Pestaña Mis Capacitaciones -->)', '', c, flags=re.DOTALL)

# Also there's some JS that mentions password_form
#     {% elif password_form.errors %}
#         new bootstrap.Tab(document.getElementById('change-password-tab')).show();
#         localStorage.setItem('activeProfileTab', '#change-password');
js_to_remove = '''    {% elif password_form.errors %}
        new bootstrap.Tab(document.getElementById('change-password-tab')).show();
        localStorage.setItem('activeProfileTab', '#change-password');'''
c = c.replace(js_to_remove, '')

with codecs.open('templates/usuarios/perfil.html', 'w', 'utf-8') as f:
    f.write(c)
