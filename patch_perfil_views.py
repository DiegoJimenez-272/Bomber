import codecs
import re

with codecs.open('usuarios/views.py', 'r', 'utf-8') as f:
    c = f.read()

c = c.replace('    password_form = PasswordChangeForm(user)\n\n', '\n')

change_password_block = '''        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Importante para mantener al usuario logueado
                messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
                return redirect('perfil')
            else:
                messages.error(request, 'Error al cambiar la contraseña. Por favor, revisa los errores.')'''

# Using regex to remove it safely regardless of leading newlines/spaces
c = re.sub(r'\s*elif \'change_password\' in request\.POST:.*?(?=^\s*$|^\s*capacitaciones_asistidas =)', '\n\n', c, flags=re.MULTILINE|re.DOTALL)

# And remove password_form from context
c = re.sub(r'\s*\'password_form\': password_form,\s*', '\n', c)

with codecs.open('usuarios/views.py', 'w', 'utf-8') as f:
    f.write(c)
