from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm as AuthPasswordChangeForm
from django.db.models import Sum, Case, When, DecimalField, F
from .models import Usuario, Compania, Rol, Proyecto, Documento, SalidaTerreno, Emergencia, Capacitacion, Mantenimiento, Inventario, CajaChica, Aviso, PasswordResetCode

class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        label=False,
        widget=forms.EmailInput(attrs={ # Se renderiza manualmente en la plantilla
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        })
    )
    nombre = forms.CharField(
        label=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control me-1', # Se renderiza manualmente en la plantilla
            'placeholder': 'Nombre'
        })
    )
    apellido = forms.CharField(
        label=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', # Se renderiza manualmente en la plantilla
            'placeholder': 'Apellido'
        })
    )
    rut = forms.CharField(
        label=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'RUT (ej: 12345678-9)'
        })
    )
    clave_radial = forms.CharField(
        label=False,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Clave Radial (ej: 1-1, 02)'
        })
    )
    compania = forms.ModelChoiceField(
        label=False,
        queryset=Compania.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}), # Se renderiza manualmente en la plantilla
        required=False,
        empty_label="Selecciona tu compañía (opcional)"
    )
    foto_perfil = forms.ImageField(
        label="Foto de Perfil (Opcional)",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'rut', 'clave_radial', 'email', 'compania', 'foto_perfil', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.nombre = self.cleaned_data['nombre']
        user.apellido = self.cleaned_data['apellido']
        user.rut = self.cleaned_data['rut']
        user.clave_radial = self.cleaned_data.get('clave_radial')
        user.compania = self.cleaned_data.get('compania')
        # El campo de la foto se maneja directamente por el ModelForm,
        # pero lo asignamos explícitamente si es necesario.
        user.foto_perfil = self.cleaned_data.get('foto_perfil')
        if commit:
            user.save()
        return user
    
    def __init__(self, *args, **kwargs):
        super(RegistroForm, self).__init__(*args, **kwargs)
        # Este código se ejecuta después de que el formulario se ha inicializado (y posiblemente validado).
        # Si hay errores, los recorremos y añadimos la clase 'is-invalid' de Bootstrap al widget del campo correspondiente.
        if self.errors:
            for field_name in self.errors:
                if field_name in self.fields:
                    # Obtiene las clases existentes o un string vacío si no hay ninguna.
                    existing_classes = self.fields[field_name].widget.attrs.get('class', '')
                    self.fields[field_name].widget.attrs['class'] = f'{existing_classes} is-invalid'.strip()

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )

class AdminUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")

    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'rut', 'clave_radial', 'email', 'rol', 'compania', 'is_active', 'is_superuser']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rol'].queryset = Rol.objects.all()
        self.fields['rol'].required = False
        self.fields['compania'].queryset = Compania.objects.all()
        self.fields['compania'].required = False
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

        # Añadir clase 'is-invalid' a los campos con errores
        if self.errors:
            for field_name in self.errors:
                if field_name in self.fields:
                    existing_classes = self.fields[field_name].widget.attrs.get('class', '')
                    self.fields[field_name].widget.attrs['class'] = f'{existing_classes} is-invalid'.strip()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class AdminUserChangeForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'rut', 'clave_radial', 'email', 'rol', 'compania', 'is_active', 'is_superuser']

    def __init__(self, *args, **kwargs):
        # Sacamos 'request' de kwargs para que no interfiera con el __init__ del padre
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.fields['rol'].queryset = Rol.objects.all()
        self.fields['rol'].required = False
        self.fields['compania'].queryset = Compania.objects.all()
        self.fields['compania'].required = False
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'
        
        # Añadir clase 'is-invalid' a los campos con errores
        if self.errors:
            for field_name in self.errors:
                if field_name in self.fields:
                    existing_classes = self.fields[field_name].widget.attrs.get('class', '')
                    self.fields[field_name].widget.attrs['class'] = f'{existing_classes} is-invalid'.strip()

        # Usar 'readonly' en lugar de 'disabled' asegura que el navegador sí envíe
        # el valor en la solicitud POST, evitando que el RUT se guarde en blanco.
        self.fields['rut'].widget.attrs['readonly'] = True
        self.fields['rut'].widget.attrs['class'] = self.fields['rut'].widget.attrs.get('class', '') + ' bg-light text-muted'

class RolForm(forms.ModelForm):
    class Meta:
        model = Rol
        fields = [
            'nombre', 'descripcion',
            'ver_resumen_general', 'ver_documentacion', 'ver_escanear_qr', 'ver_inventario',
            'ver_salidas_terreno', 'ver_emergencias', 'ver_capacitaciones', 'ver_mantenimientos', 'ver_proyectos', 'ver_caja_chica',
            'ver_avisos', 'editar_documentacion', 'editar_inventario', 'editar_salidas_terreno',
            'editar_emergencias', 'editar_capacitaciones', 'editar_mantenimientos', 'editar_proyectos', 'editar_caja_chica', 'editar_avisos'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Capitán', 'list': 'roles-sugeridos'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción de las responsabilidades del rol'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar la clase form-check-input para que se rendericen como Switches
        permisos_fields = [
            'ver_resumen_general', 'ver_documentacion', 'ver_escanear_qr', 'ver_inventario',
            'ver_salidas_terreno', 'ver_emergencias', 'ver_capacitaciones', 'ver_mantenimientos', 'ver_proyectos', 'ver_caja_chica',
            'ver_avisos', 'editar_documentacion', 'editar_inventario', 'editar_salidas_terreno',
            'editar_emergencias', 'editar_capacitaciones', 'editar_mantenimientos', 'editar_proyectos', 'editar_caja_chica', 'editar_avisos'
        ]
        for field in permisos_fields:
            self.fields[field].widget.attrs.update({'class': 'form-check-input'})

class CompaniaForm(forms.ModelForm):
    generar_inventario = forms.BooleanField(
        label="Añadir inventario base automáticamente",
        required=False,
        initial=True,
        help_text="Creará cascos, botas, mangueras, etc., por defecto para esta compañía."
    )

    class Meta:
        model = Compania
        fields = ['nombre', 'ubicacion', 'logo', 'generar_inventario']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Primera Compañía'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Av. Principal 123, Ciudad'}),
            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }




class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'presupuesto', 'responsable', 'tipo', 'prioridad']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Construcción de nuevo cuartel'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describa el proyecto y su alcance'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'presupuesto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 5000000'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'prioridad': forms.NumberInput(attrs={'class': 'form-range', 'type': 'range', 'min': '0', 'max': '100'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['responsable'].queryset = Usuario.objects.all()
        self.fields['responsable'].empty_label = "Seleccionar responsable"
        self.fields['responsable'].required = False # Hacemos que este campo no sea obligatorio
        
        if self.errors:
            for field_name in self.errors:
                if field_name in self.fields:
                    existing_classes = self.fields[field_name].widget.attrs.get('class', '')
                    self.fields[field_name].widget.attrs['class'] = f'{existing_classes} is-invalid'.strip()

class CajaChicaForm(forms.ModelForm):
    class Meta:
        model = CajaChica
        fields = ['tipo', 'monto', 'descripcion', 'documento_adjunto', 'compania']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Monto en CLP', 'step': '0.01'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Compra de artículos de limpieza'}),
            'documento_adjunto': forms.FileInput(attrs={'class': 'form-control'}),
            'compania': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['documento_adjunto'].required = False
        
        if self.user and not self.user.is_superuser:
            if 'compania' in self.fields:
                del self.fields['compania']
        elif 'compania' in self.fields:
            self.fields['compania'].queryset = Compania.objects.all()
            self.fields['compania'].empty_label = "Caja General (Visible por todos)"
            self.fields['compania'].required = False
            
        if self.errors:
            for field_name in self.errors:
                if field_name in self.fields:
                    existing_classes = self.fields[field_name].widget.attrs.get('class', '')
                    self.fields[field_name].widget.attrs['class'] = f'{existing_classes} is-invalid'.strip()
        # Para el RadioSelect, necesitamos un widget personalizado o manejarlo en la plantilla.
        # Por simplicidad, lo dejaremos así y ajustaremos la plantilla.

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

class ArchivoProyectoForm(forms.Form):
    archivos = MultipleFileField(
        widget=MultipleFileInput(attrs={'class': 'form-control', 'name': 'archivos'}),
        required=False
    )

class DocumentoForm(forms.ModelForm):
    class Meta:
        model = Documento
        fields = ['nombre', 'descripcion', 'archivo', 'compania']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del documento'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción breve (opcional)'}),
            'archivo': forms.FileInput(attrs={'class': 'form-control'}),
            'compania': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Ocultar el campo compañía a usuarios normales
        if self.user and not self.user.is_superuser:
            if 'compania' in self.fields:
                del self.fields['compania']
        elif 'compania' in self.fields:
            self.fields['compania'].queryset = Compania.objects.all()
                    self.fields['compania'].empty_label = "Solo Administración (Oculto a todos)"
            self.fields['compania'].required = False
class PerfilForm(forms.ModelForm):
    foto_perfil = forms.ImageField(
        label="Cambiar foto de perfil",
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )

    class Meta:
        model = Usuario
        fields = ['foto_perfil', 'nombre', 'apellido', 'email', 'clave_radial']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'clave_radial': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.errors:
            for field_name in self.errors:
                if field_name in self.fields:
                    self.fields[field_name].widget.attrs['class'] += ' is-invalid'

class PasswordChangeForm(AuthPasswordChangeForm):
    old_password = forms.CharField(
        label="Contraseña actual",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Introduce tu contraseña actual'}),
    )
    new_password1 = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Introduce tu nueva contraseña'}),
    )
    new_password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirma tu nueva contraseña'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].help_text = None

class SalidaTerrenoForm(forms.ModelForm):
    class Meta:
        model = SalidaTerreno
        fields = ['motivo', 'direccion', 'fecha_hora_salida', 'fecha_hora_regreso', 'unidades_involucradas', 'kilometraje_salida', 'kilometraje_regreso', 'personal_a_cargo', 'descripcion']
        widgets = {
            'motivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 10-0-1 (Llamado estructural)'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Calle Falsa 123, Comuna'}),
            'fecha_hora_salida': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'fecha_hora_regreso': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'unidades_involucradas': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'B-1, R-2...'}),
            'kilometraje_salida': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Km al salir del cuartel'}),
            'kilometraje_regreso': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Km al regresar al cuartel'}),
            'personal_a_cargo': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detalles del servicio, novedades, etc.'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['personal_a_cargo'].queryset = Usuario.objects.filter(is_active=True).order_by('nombre')
        self.fields['personal_a_cargo'].empty_label = "Seleccionar responsable"

        if self.errors:
            for field_name in self.errors:
                if field_name in self.fields:
                    existing_classes = self.fields[field_name].widget.attrs.get('class', '')
                    self.fields[field_name].widget.attrs['class'] = f'{existing_classes} is-invalid'.strip()

class EmergenciaForm(forms.ModelForm):
    class Meta:
        model = Emergencia
        fields = ['tipo', 'direccion', 'fecha_hora_alarma', 'descripcion', 'unidades_despachadas', 'oficial_a_cargo', 'estado']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Calle Falsa 123, Comuna'}),
            'fecha_hora_alarma': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Detalles del incidente, puntos de referencia, etc.'}),
            'unidades_despachadas': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'B-1, R-2...'}),
            'oficial_a_cargo': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['oficial_a_cargo'].queryset = Usuario.objects.filter(is_active=True).order_by('nombre')
        self.fields['oficial_a_cargo'].empty_label = "Seleccionar oficial a cargo"

        if self.errors:
            for field_name in self.errors:
                if field_name in self.fields:
                    existing_classes = self.fields[field_name].widget.attrs.get('class', '')
                    self.fields[field_name].widget.attrs['class'] = f'{existing_classes} is-invalid'.strip()

class CapacitacionForm(forms.ModelForm):
    enviar_invitacion = forms.BooleanField(
        label="Enviar invitación como notificación",
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    audiencia = forms.ChoiceField(
        label="¿A quién invitar?",
        choices=[
            ('general', 'General (Todos los miembros activos)'),
            ('especificos', 'Solo a los asistentes seleccionados abajo')
        ],
        initial='general',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        required=False
    )

    class Meta:
        model = Capacitacion
        fields = ['nombre', 'malla', 'descripcion', 'fecha_inicio', 'fecha_fin', 'lugar', 'instructor', 'cupos', 'companias_invitadas', 'asistentes']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Curso de Rescate Vehicular Nivel I'}),
            'malla': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Objetivos, temas a tratar, etc.'}),
            'fecha_inicio': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'fecha_fin': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Cuartel General, Campo de entrenamiento'}),
            'instructor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del instructor o entidad'}),
            'cupos': forms.NumberInput(attrs={'class': 'form-control'}),
            'asistentes': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
            'companias_invitadas': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input comp-filter-cb'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['asistentes'].queryset = Usuario.objects.filter(is_active=True).order_by('nombre')
        self.fields['asistentes'].required = False
        self.fields['companias_invitadas'].queryset = Compania.objects.all().order_by('nombre')
        self.fields['companias_invitadas'].required = False
        self.fields['fecha_fin'].required = False
        self.fields['cupos'].required = False

        # Agregar clases a los radios
        for _, radio in self.fields['audiencia'].choices:
            pass # Radios se manejan en la plantilla

        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                field.widget.attrs['class'] += ' is-invalid'

class MantenimientoForm(forms.ModelForm):
    caja_descuento = forms.ChoiceField(
        label="Cuenta de Origen",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Mantenimiento
        fields = ['fecha', 'fecha_resolucion', 'vehiculo', 'costo', 'tipo', 'responsable', 'descripcion']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_resolucion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'vehiculo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Toyota - ABC123'}),
            'costo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa el monto total', 'step': '0.01'}),
            'tipo': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'responsable': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe detalladamente el mantenimiento realizado...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if not self.instance.pk:
            opciones_caja = [('', 'Seleccionar caja a descontar...')]
            opciones_caja.append(('sin_costo', 'Sin costo / No aplica'))
            opciones_caja.append(('general', 'Caja General (Global)'))
            for c in Compania.objects.all():
                opciones_caja.append((str(c.id), f'Caja {c.nombre}'))
            self.fields['caja_descuento'].choices = opciones_caja
        elif 'caja_descuento' in self.fields:
            del self.fields['caja_descuento']

        self.fields['responsable'].queryset = Usuario.objects.filter(is_active=True).order_by('nombre')
        self.fields['responsable'].empty_label = "Seleccionar responsable"
        self.fields['responsable'].required = True

        if self.errors:
            for field_name in self.errors:
                if field_name in self.fields:
                    # Para RadioSelect, el error se maneja mejor en la plantilla
                    if not isinstance(self.fields[field_name].widget, forms.RadioSelect):
                        existing_classes = self.fields[field_name].widget.attrs.get('class', '')
                        self.fields[field_name].widget.attrs['class'] = f'{existing_classes} is-invalid'.strip()

    def clean(self):
        cleaned_data = super().clean()
        costo = cleaned_data.get('costo')
        responsable = cleaned_data.get('responsable')
        caja_descuento = cleaned_data.get('caja_descuento')

        if not self.instance.pk and costo and costo > 0:
            if not caja_descuento:
                self.add_error('caja_descuento', 'Debe seleccionar una Cuenta de Origen para descontar los fondos.')
                self.add_error('costo', 'Falta seleccionar la Cuenta de Origen (verifique que el campo exista en el formulario HTML).')
            elif caja_descuento != 'sin_costo':
                compania_q = Compania.objects.filter(id=int(caja_descuento)).first() if caja_descuento != 'general' else None
                saldo_dict = CajaChica.objects.filter(compania=compania_q).aggregate(
                    saldo=Sum(Case(When(tipo='Ingreso', then=F('monto')), When(tipo='Egreso', then=-F('monto')), output_field=DecimalField()))
                )
                saldo = saldo_dict['saldo'] or 0
                if saldo < costo:
                    nombre_caja = f"la Caja {compania_q.nombre}" if compania_q else "la Caja General"
                    self.add_error('costo', f'Fondos insuficientes en {nombre_caja}. Saldo actual disponible: ${saldo:,.0f}')
        
        return cleaned_data

class ArchivoMantenimientoForm(forms.Form):
    archivos = MultipleFileField(
        label="Documentos adjuntos",
        widget=MultipleFileInput(attrs={
            'class': 'form-control', 
            'id': 'file-upload' # Coincide con el label del HTML
        }),
        required=False
    )

class InventarioForm(forms.ModelForm):
    cantidad = forms.IntegerField(min_value=1, initial=1, label="Cantidad a registrar", widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Inventario
        # 'cantidad' del formulario no es el del modelo, lo sacamos de fields
        fields = ['nombre', 'compania', 'ubicacion', 'estado', 'fecha_adquisicion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'list': 'datalist-items', 'placeholder': 'Ej: Casco de bombero, Motosierra...'}),
            'compania': forms.Select(attrs={'class': 'form-select'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Bodega 1, Carro B-2'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'fecha_adquisicion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['fecha_adquisicion'].required = False
        
        if self.user and not self.user.is_superuser:
            if 'compania' in self.fields:
                del self.fields['compania']
        elif 'compania' in self.fields:
            self.fields['compania'].queryset = Compania.objects.all()
            self.fields['compania'].empty_label = "Seleccionar compañía"

        if self.errors:
            for field_name in self.errors:
                if field_name in self.fields:
                    existing_classes = self.fields[field_name].widget.attrs.get('class', '')
                    self.fields[field_name].widget.attrs['class'] = f'{existing_classes} is-invalid'.strip()

class InventarioEditForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ['nombre', 'compania', 'asignado_a', 'ubicacion', 'estado', 'fecha_adquisicion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'list': 'datalist-items', 'placeholder': 'Ej: Casco de bombero, Motosierra...'}),
            'compania': forms.Select(attrs={'class': 'form-select'}),
            'asignado_a': forms.Select(attrs={'class': 'form-select'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'fecha_adquisicion': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar usuarios por la compañía a la que pertenece el ítem
        if self.instance and self.instance.pk and self.instance.compania:
            self.fields['asignado_a'].queryset = Usuario.objects.filter(is_active=True, compania=self.instance.compania).order_by('nombre')
        else:
            self.fields['asignado_a'].queryset = Usuario.objects.filter(is_active=True).order_by('nombre')
            
        self.fields['asignado_a'].empty_label = "Sin asignar / Bodega"
        self.fields['asignado_a'].required = False
        self.fields['fecha_adquisicion'].required = False
        
        if self.user and not self.user.is_superuser:
            if 'compania' in self.fields:
                del self.fields['compania']
        elif 'compania' in self.fields:
            self.fields['compania'].queryset = Compania.objects.all()
            self.fields['compania'].empty_label = "Seleccionar compañía"

class InventarioGroupEditForm(forms.Form):
    ubicacion = forms.CharField(
        label="Nueva Ubicación",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Bodega 2, Carro B-1'})
    )
    estado = forms.ChoiceField(
        label="Nuevo Estado",
        choices=Inventario.ESTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class AvisoForm(forms.ModelForm):
    usuarios = forms.ModelMultipleChoiceField(
        queryset=Usuario.objects.filter(is_active=True).order_by('nombre'),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label="Seleccionar Destinatarios"
    )

    class Meta:
        model = Aviso
        fields = ['titulo', 'mensaje']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Reunión Extraordinaria o Aviso Importante'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Escribe el mensaje del aviso...'}),
        }

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingresa tu correo electrónico'})
    )

class PasswordResetVerifyForm(forms.Form):
    codigo = forms.CharField(
        max_length=6, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código de 6 dígitos', 'autocomplete': 'off'})
    )

class PasswordResetNewPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nueva contraseña'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar nueva contraseña'}))

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', 'Las contraseñas no coinciden.')
        return cleaned_data
