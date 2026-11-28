import json
from datetime import datetime
from decimal import Decimal

from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone

from .models import (
    CajaChica,
    Emergencia,
    EmergenciaUnidad,
    RegistroOperativo,
    RegistroOperativoUnidad,
    RondaVehiculo,
    SalidaTerreno,
    SalidaTerrenoUnidad,
    Usuario,
    Vehiculo,
)


RONDAS_CHECKLIST = [
    ('direccion', 'Sistema de dirección', ['En buen estado', 'En mal estado']),
    ('niveles', 'Niveles de aceite de motor y refrigerante', ['Buen nivel ambos', 'Bajo aceite motor', 'Bajo refrigerante']),
    ('frenos', 'Frenos de servicio, pedal y retardo', ['Sí', 'No']),
    ('luces', 'Luces generales', ['Sí', 'No']),
    ('neumaticos', 'Neumáticos', ['Sí', 'No']),
    ('tablero', 'Tablero sin testigos de falla (motor, ABS, aceite)', ['Sí', 'No']),
    ('cinturones', 'Cinturones de seguridad', ['Sí', 'No']),
    ('radio', 'Radio de comunicación', ['Sí', 'No']),
    ('bocinas', 'Bocinas y aparato sonoro', ['Sí', 'No']),
    ('asiento', 'Asiento del conductor', ['Sí', 'No']),
    ('puertas', 'Puertas y cabina', ['Sí', 'No']),
    ('extintor', 'Extintor operativo de 10 kg', ['Sí', 'No']),
    ('espejos', 'Espejos retrovisores', ['Sí', 'No']),
    ('vidrios', 'Vidrios y parabrisas', ['Sí', 'No']),
    ('limpiaparabrisas', 'Limpiaparabrisas', ['Sí', 'No']),
    ('retroceso', 'Alarma sonora de retroceso', ['Sí', 'No']),
    ('seguridad', 'Cuñas, triángulos y conos', ['Sí', 'No']),
    ('climatizacion', 'Calefacción y aire acondicionado', ['Sí', 'No']),
    ('estructura', 'Chasis, barandas, gavetas, cortinas, escaleras y soportes', ['Sí', 'No']),
    ('documentacion', 'Documentación de la unidad al día', ['Sí', 'No']),
]

TIPOS_EMERGENCIA = {'emergencia', 'emergencia_vehicular'}
TIPOS_CON_KILOMETRAJE = {
    'emergencia', 'emergencia_vehicular', 'servicio_especial',
    'practica_maquinista', 'rodaje', 'se_dirige_6_13', 'rodaje_6_13', 'combustible_6_14',
}
TIPOS_CON_NOVEDADES = {
    'emergencia', 'emergencia_vehicular', 'servicio_especial',
    'practica_maquinista', 'rodaje', 'se_dirige_6_13', 'rodaje_6_13',
}

FAMILIAS_CLAVES_EMERGENCIA = [
    ('10-0', '10-0 · Emergencias estructurales'),
    ('10-1', '10-1 · Llamado a vehículos'),
    ('10-2', '10-2 · Pastizales y/o basura'),
    ('10-3', '10-3 · Rescate de emergencia'),
    ('10-4', '10-4 · Rescate vehicular'),
    ('10-5', '10-5 · Hazmat'),
    ('10-6', '10-6 · Emanación de gas'),
    ('10-7', '10-7 · Llamado eléctrico'),
    ('10-8', '10-8 · Llamado no clasificado'),
    ('10-9', '10-9 · Otros servicios'),
    ('10-10', '10-10 · Rebrote de fuego'),
    ('otros', 'Otros llamados'),
]

CLAVES_POR_FAMILIA = {
    '10-0': [
        ('10-0', '10-0 · Llamado estructural'),
        ('10-0-1', '10-0-1 · Llamado estructural básico (hasta 3 pisos)'),
        ('10-0-2', '10-0-2 · Llamado estructural edificio (4 o más pisos)'),
        ('10-0-3', '10-0-3 · Llamado estructural lugar público'),
        ('10-0-4', '10-0-4 · Llamado estructural industrial'),
        ('10-0-5', '10-0-5 · Llamado estructural Hazmat'),
        ('10-0-7', '10-0-7 · Inflamación de chimenea o ducto'),
        ('10-0-15', '10-0-15 · Llamado estructural rural'),
    ],
    '10-1': [
        ('10-1-1', '10-1-1 · Incendio de vehículo menor'),
        ('10-1-2', '10-1-2 · Incendio de vehículo de carga'),
        ('10-1-3', '10-1-3 · Incendio de vehículo con pasajeros'),
        ('10-1-4', '10-1-4 · Maquinaria agrícola, pesada o forestal'),
        ('10-1-5', '10-1-5 · Incendio de aeronave'),
        ('10-1-6', '10-1-6 · Incendio en vehículo a gas'),
        ('10-1-7', '10-1-7 · Incendio en vehículo eléctrico'),
    ],
    '10-2': [
        ('10-2-1', '10-2-1 · Incendio vegetacional urbano'),
        ('10-2-2', '10-2-2 · Incendio vegetacional rural'),
        ('10-2-3', '10-2-3 · Incendio de sembrado agrícola'),
        ('10-2-4', '10-2-4 · Incendio de microbasurales, desechos o escombros'),
        ('10-2-6', '10-2-6 · Vertedero'),
    ],
    '10-3': [('10-3', '10-3 · Rescate de persona (indicar situación)')],
    '10-4': [
        ('10-4-1', '10-4-1 · Rescate vehicular de vehículo menor'),
        ('10-4-2', '10-4-2 · Rescate de vehículo de carga, maquinaria o transporte'),
        ('10-4-3', '10-4-3 · Rescate vehicular en desnivel, aguas o quebradas'),
        ('10-4-4', '10-4-4 · Rescate vehicular de vehículos de emergencia'),
        ('10-4-5', '10-4-5 · Rescate vehicular relacionado con Hazmat'),
        ('10-4', '10-4 · Rescate vehicular (histórico)'),
    ],
    '10-5': [
        ('10-5-1', '10-5-1 · Derrame de hidrocarburos'),
        ('10-5-2', '10-5-2 · Incidente con materiales peligrosos'),
        ('10-5-3', '10-5-3 · Atentado químico, biológico, radiológico o equivalente'),
    ],
    '10-6': [
        ('10-6-1', '10-6-1 · Emanación de gas combustible'),
        ('10-6-2', '10-6-2 · Explosión de gas'),
        ('10-6-3', '10-6-3 · Explosión de gas con fuego'),
        ('10-6', '10-6 · Emanación de gas (histórico)'),
    ],
    '10-7': [
        ('10-7-1', '10-7-1 · Eléctrico habitacional, comercial o industrial'),
        ('10-7-2', '10-7-2 · Eléctrico en cámara, transformador o subestación'),
        ('10-7', '10-7 · Riesgo eléctrico (histórico)'),
    ],
    '10-8': [
        ('10-8', '10-8 · Llamado no clasificado'),
        ('10-8-8', '10-8-8 · Rastreo de personas en sectores urbanos/rurales'),
        ('10-8-10', '10-8-10 · Rastreo superficial en cauces o aguas abiertas'),
        ('10-8-11', '10-8-11 · Recuperación de cadáveres'),
        ('10-8-12', '10-8-12 · Instrucción, asesorías o capacitación'),
        ('10-8-13', '10-8-13 · Caída de árbol'),
        ('10-8-14', '10-8-14 · Voladura de techo o temporal de viento'),
        ('10-8-15', '10-8-15 · Extracción de agua por inundación'),
        ('10-8-16', '10-8-16 · Rescate animal'),
        ('10-8-18', '10-8-18 · Lavado de carreteras (derrames)'),
    ],
    '10-9': [
        ('10-9-1', '10-9-1 · Peritaje solicitado por el Ministerio Público'),
        ('10-9-2', '10-9-2 · Revisión de edificios'),
        ('10-9-3', '10-9-3 · Inspección de local comercial'),
        ('10-9-4', '10-9-4 · Inspección de industrias'),
        ('10-9-5', '10-9-5 · Inspección de grifo'),
        ('10-9-6', '10-9-6 · Simulacros o ejercicios a terceros'),
        ('10-9-7', '10-9-7 · Monitoreo / inspección'),
        ('10-9-19', '10-9-19 · Instrucción, asesorías o capacitación'),
    ],
    '10-10': [
        ('10-10-1', '10-10-1 · Rebrote estructural'),
        ('10-10-2', '10-10-2 · Rebrote forestal'),
        ('10-10', '10-10 · Rebrote de fuego (histórico)'),
    ],
    'otros': [
        ('10-11', '10-11 · Servicio o accidente aéreo'),
        ('10-12', '10-12 · Apoyo a otros Cuerpos'),
        ('10-13', '10-13 · Artefacto explosivo o acto terrorista'),
        ('10-14', '10-14 · Accidente de aviación'),
        ('9-3', '9-3 · Acuartelamiento general (histórico)'),
        ('9-4', '9-4 · Acuartelamiento preventivo (histórico)'),
        ('otro', 'Otro'),
    ],
}


class RegistroOperativoForm(forms.ModelForm):
    codigo = forms.ChoiceField(label='Código / tipo', choices=(), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    familia_codigo = forms.ChoiceField(label='Familia de clave', choices=FAMILIAS_CLAVES_EMERGENCIA, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    detalle_codigo = forms.CharField(label='Especifica el tipo "Otro"', required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'maxlength': 255}))
    instituciones_apoyo = forms.MultipleChoiceField(
        label='Apoyo de otras instituciones', choices=RegistroOperativo.APOYO_CHOICES,
        required=False, widget=forms.CheckboxSelectMultiple,
    )
    autorizaciones = forms.MultipleChoiceField(
        label='Autorización histórica', choices=[('6', '6'), ('7', '7'), ('1', '1'), ('2', '2')],
        required=False, widget=forms.MultipleHiddenInput,
    )
    autorizado_por = forms.ModelMultipleChoiceField(
        label='Autorizado por', queryset=Usuario.objects.none(), required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    involucrados_json = forms.CharField(required=False, widget=forms.HiddenInput())
    checklist_json = forms.CharField(required=False, widget=forms.HiddenInput())
    emergencia_activa = forms.ModelChoiceField(
        label='Emergencia activa / código', queryset=Emergencia.objects.none(), required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    asistentes = forms.ModelMultipleChoiceField(
        label='Voluntarios asistentes', queryset=Usuario.objects.none(), required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    unidades = forms.ModelMultipleChoiceField(
        label='Carros / unidades', queryset=Vehiculo.objects.none(), required=False,
        widget=forms.MultipleHiddenInput,
    )
    asistencia_unidades = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = RegistroOperativo
        fields = [
            'tipo', 'codigo', 'fecha_inicio', 'fecha_termino', 'hora_despacho', 'hora_llegada',
            'kilometraje_despacho', 'kilometraje_llegada', 'direccion', 'estacion_servicio',
            'estacion_detalle', 'vehiculo', 'maquinista', 'obac', 'obac_voluntario', 'apoyo_otro_cuerpo',
            'instituciones_apoyo', 'apoyo_otros', 'informe', 'novedades_unidad', 'lesionados_externos',
            'aspirante_nombre', 'aspirante_clave', 'aspirante_voluntario', 'instructor', 'combustible_tipo',
            'monto_combustible', 'autorizaciones', 'autorizado_por', 'asistentes', 'unidades', 'asistencia_unidades',
            'familia_codigo', 'detalle_codigo',
        ]
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo_operativo'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_termino': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_despacho': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_llegada': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'kilometraje_despacho': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 1, 'inputmode': 'numeric'}),
            'kilometraje_llegada': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 1, 'inputmode': 'numeric'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'estacion_servicio': forms.Select(attrs={'class': 'form-select', 'id': 'id_estacion_servicio'}),
            'estacion_detalle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la estación'}),
            'vehiculo': forms.HiddenInput(),
            'maquinista': forms.Select(attrs={'class': 'form-select'}),
            'obac': forms.HiddenInput(),
            'obac_voluntario': forms.Select(attrs={'class': 'form-select'}),
            'apoyo_otro_cuerpo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Cuerpo de Bomberos'}),
            'apoyo_otros': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especifica la institución'}),
            'informe': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'novedades_unidad': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Indica las novedades o “Sin novedad”'}),
            'lesionados_externos': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Nombre y RUT'}),
            'aspirante_nombre': forms.HiddenInput(),
            'aspirante_clave': forms.HiddenInput(),
            'aspirante_voluntario': forms.Select(attrs={'class': 'form-select'}),
            'instructor': forms.Select(attrs={'class': 'form-select'}),
            'combustible_tipo': forms.Select(attrs={'class': 'form-select'}),
            'monto_combustible': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '1', 'inputmode': 'decimal'}),
        }

    CODIGOS = {
        'emergencia': [choice for family in FAMILIAS_CLAVES_EMERGENCIA for choice in CLAVES_POR_FAMILIA[family[0]]],
        'emergencia_vehicular': CLAVES_POR_FAMILIA['10-4'],
        'servicio_especial': [
            ('reunion_superintendencia', 'Reunión de Superintendencia'),
            ('reunion_comandancia', 'Reunión de Comandancia'),
            ('actividad_entidad', 'Actividad solicitada por otra entidad'),
            ('simulacro', 'Simulacro'), ('otro', 'Otro'),
        ],
        'practica_maquinista': [('6-18', '6-18 — Práctica de aspirante a maquinista')],
        'rodaje': [('', 'Rodaje (sin clave)')],
        'se_dirige_6_13': [('6-13', '6-13 — Se dirige a')],
        'rodaje_6_13': [('6-13', '6-13 — Registro histórico: Se dirige a / Rodaje')],
        'combustible_6_14': [('6-14', '6-14 — Carga de combustible')],
        'ronda_maquinistas': [('ronda_maquinistas', 'Ronda de maquinistas')],
        'llegada_cuartel': [('llegada_cuartel', 'Voluntarios llegados al cuartel')],
    }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        rol = getattr(user, 'rol', None)
        puede_emergencias = bool(user and (user.is_superuser or (rol and rol.editar_emergencias)))
        puede_salidas = bool(user and (user.is_superuser or (rol and rol.editar_salidas_terreno)))
        tipos_disponibles = [
            choice for choice in RegistroOperativo.TIPO_CHOICES
            if choice[0] != 'rodaje_6_13' and (
                (choice[0] in TIPOS_EMERGENCIA or choice[0] == 'llegada_cuartel') and puede_emergencias
            or (choice[0] not in TIPOS_EMERGENCIA and choice[0] != 'llegada_cuartel') and puede_salidas
            )
        ]
        self.fields['tipo'].choices = tipos_disponibles
        if tipos_disponibles and not self.is_bound:
            self.fields['tipo'].initial = tipos_disponibles[0][0]
        tipo = (self.data.get('tipo') if self.is_bound else self.initial.get('tipo')) or 'emergencia'
        familias_disponibles = [('10-4', dict(FAMILIAS_CLAVES_EMERGENCIA)['10-4'])] if tipo == 'emergencia_vehicular' else (
            FAMILIAS_CLAVES_EMERGENCIA if tipo == 'emergencia' else []
        )
        self.fields['familia_codigo'].choices = [('', 'Seleccionar familia')] + familias_disponibles
        familia = (self.data.get('familia_codigo') if self.is_bound else self.initial.get('familia_codigo')) or ''
        if tipo == 'emergencia_vehicular' and not familia:
            familia = '10-4'
            self.fields['familia_codigo'].initial = familia
        if tipo in TIPOS_EMERGENCIA:
            codigos = list(CLAVES_POR_FAMILIA.get(familia, []))
            if tipo == 'emergencia_vehicular':
                codigos = list(CLAVES_POR_FAMILIA['10-4'])
        else:
            codigos = list(self.CODIGOS.get(tipo, []))
        codigo_actual = getattr(self.instance, 'codigo', '')
        if self.instance.pk and codigo_actual and all(valor != codigo_actual for valor, _ in codigos):
            codigos.append((codigo_actual, f'{codigo_actual} — Código histórico'))
        self.fields['codigo'].choices = [('', 'Seleccionar')] + codigos
        self.fields['vehiculo'].queryset = Vehiculo.objects.select_related('compania').order_by('compania__nombre', 'nombre')
        self.fields['unidades'].queryset = self.fields['vehiculo'].queryset
        miembros = Usuario.objects.miembros_activos().select_related('compania').order_by('clave_radial', 'apellido', 'nombre')
        self.fields['maquinista'].queryset = miembros.filter(especialidades__slug='maquinista', especialidades__activa=True).distinct()
        self.fields['instructor'].queryset = miembros
        self.fields['obac_voluntario'].queryset = miembros
        self.fields['aspirante_voluntario'].queryset = miembros.filter(especialidades__slug='aspirante_maquinista', especialidades__activa=True).distinct()
        self.fields['autorizado_por'].queryset = miembros
        self.fields['asistentes'].queryset = miembros
        self.fields['maquinista'].label_from_instance = lambda usuario: usuario.nombre_operativo
        self.fields['instructor'].label_from_instance = lambda usuario: usuario.nombre_operativo
        self.fields['obac_voluntario'].label_from_instance = lambda usuario: usuario.nombre_operativo
        self.fields['aspirante_voluntario'].label_from_instance = lambda usuario: usuario.nombre_operativo
        self.fields['autorizado_por'].label_from_instance = lambda usuario: usuario.nombre_operativo
        self.fields['asistentes'].label_from_instance = lambda usuario: usuario.nombre_operativo
        if user and not user.is_superuser and user.compania_id and getattr(getattr(user, 'rol', None), 'nombre', '').strip().casefold() not in {'admin', 'administrador'}:
            self.fields['vehiculo'].queryset = self.fields['vehiculo'].queryset.filter(compania_id=user.compania_id)
            for name in ('maquinista', 'instructor', 'obac_voluntario', 'aspirante_voluntario', 'autorizado_por', 'asistentes'):
                self.fields[name].queryset = self.fields[name].queryset.filter(compania_id=user.compania_id)
        self.fields['vehiculo'].empty_label = 'Seleccionar carro'
        self.fields['maquinista'].empty_label = 'Seleccionar maquinista'
        self.fields['instructor'].empty_label = 'Seleccionar instructor'
        self.fields['obac_voluntario'].empty_label = 'Seleccionar OBAC'
        self.fields['aspirante_voluntario'].empty_label = 'Seleccionar aspirante'
        emergencias_activas = Emergencia.objects.filter(estado='Activa')
        if user and not user.is_superuser and user.compania_id and getattr(getattr(user, 'rol', None), 'nombre', '').strip().casefold() not in {'admin', 'administrador'}:
            emergencias_activas = emergencias_activas.filter(
                Q(unidades_asistencia__unidad__compania_id=user.compania_id)
            ).distinct()
        self.fields['emergencia_activa'].queryset = emergencias_activas.order_by('-fecha_hora_alarma')
        self.fields['emergencia_activa'].label_from_instance = lambda e: f'{e.get_tipo_display()} · {e.direccion or "Sin dirección"} · {e.fecha_hora_alarma.strftime("%d/%m/%Y %H:%M") if e.fecha_hora_alarma else "Sin fecha"}'
        self.fields['emergencia_activa'].empty_label = 'Seleccionar emergencia activa'
        for name in ('fecha_inicio', 'fecha_termino', 'hora_despacho', 'hora_llegada', 'kilometraje_despacho', 'kilometraje_llegada', 'direccion', 'vehiculo', 'maquinista', 'instructor', 'estacion_servicio', 'combustible_tipo', 'monto_combustible'):
            self.fields[name].required = False
        for name in ('obac_voluntario', 'aspirante_voluntario', 'autorizado_por'):
            self.fields[name].required = False
        self.fields['obac'].required = False
        self.fields['aspirante_nombre'].required = False
        self.fields['aspirante_clave'].required = False
        self.fields['detalle_codigo'].required = False
        self.fields['estacion_detalle'].required = False

    def clean_instituciones_apoyo(self):
        return list(self.cleaned_data.get('instituciones_apoyo') or [])

    def _json_list(self, field_name, label):
        raw = self.cleaned_data.get(field_name) or '[]'
        try:
            value = json.loads(raw)
        except (TypeError, ValueError):
            raise ValidationError(f'El contenido de {label} no es válido.')
        if not isinstance(value, list):
            raise ValidationError(f'El contenido de {label} debe ser una lista.')
        return value

    def clean(self):
        data = super().clean()
        tipo = data.get('tipo')
        if not tipo:
            return data

        obac = data.get('obac_voluntario')
        if obac:
            data['obac'] = obac.get_full_name()
        codigos_fijos = {
            'practica_maquinista': '6-18',
            'se_dirige_6_13': '6-13',
            'rodaje_6_13': '6-13',
            'combustible_6_14': '6-14',
        }
        if tipo in codigos_fijos:
            data['codigo'] = codigos_fijos[tipo]
        aspirante = data.get('aspirante_voluntario')
        if aspirante:
            data['aspirante_nombre'] = aspirante.get_full_name()
            data['aspirante_clave'] = (aspirante.clave_radial or '')[:40]
        if data.get('detalle_codigo'):
            detalle = f"Tipo específico: {data['detalle_codigo'].strip()}"
            data['informe'] = '\n'.join(filter(None, [data.get('informe', '').strip(), detalle]))

        unidades_limpias = list(data.get('unidades') or [])
        if not unidades_limpias and data.get('vehiculo'):
            unidades_limpias = [data['vehiculo']]
        unidades_por_id = {str(unidad.pk): unidad for unidad in unidades_limpias}
        ids_publicados = self.data.getlist('unidades') if self.is_bound else []
        unidades_ordenadas = [
            unidades_por_id[unidad_id]
            for unidad_id in ids_publicados
            if unidad_id in unidades_por_id
        ]
        if not unidades_ordenadas:
            unidades_ordenadas = unidades_limpias
        data['unidades'] = unidades_ordenadas

        vehiculo_principal = data.get('vehiculo')
        if unidades_ordenadas:
            if vehiculo_principal not in unidades_ordenadas:
                vehiculo_principal = unidades_ordenadas[0]
                data['vehiculo'] = vehiculo_principal
        elif tipo != 'llegada_cuartel':
            vehiculo_principal = None
            data['vehiculo'] = None

        try:
            asistencia_raw = self.data.get('asistencia_unidades') or '{}' if self.is_bound else '{}'
            asistencia_parseada = json.loads(asistencia_raw)
            if not isinstance(asistencia_parseada, dict):
                raise ValueError
            asistencia_normalizada = {}
            for unidad_id, asistentes_ids in asistencia_parseada.items():
                unidad_id = str(int(unidad_id))
                if not isinstance(asistentes_ids, list):
                    raise ValueError
                asistencia_normalizada[unidad_id] = list(dict.fromkeys(int(pk) for pk in asistentes_ids))
        except (TypeError, ValueError, json.JSONDecodeError):
            asistencia_normalizada = {}
            self.add_error('asistencia_unidades', 'No se pudo leer la asistencia de los carros seleccionados.')

        ids_unidades_seleccionadas = {str(unidad.pk) for unidad in unidades_ordenadas}
        if tipo == 'llegada_cuartel' and asistencia_normalizada:
            self.add_error('asistencia_unidades', 'La llegada al cuartel no utiliza asistencia por carro.')
        elif set(asistencia_normalizada) - ids_unidades_seleccionadas:
            self.add_error('asistencia_unidades', 'La asistencia incluye un carro que no está seleccionado.')
        asistentes_por_unidad = [pk for ids in asistencia_normalizada.values() for pk in ids]
        if len(asistentes_por_unidad) != len(set(asistentes_por_unidad)):
            self.add_error('asistencia_unidades', 'Un voluntario no puede quedar asignado a más de un carro en el mismo registro.')
        ids_asistentes_validos = set(self.fields['asistentes'].queryset.values_list('pk', flat=True))
        if set(asistentes_por_unidad) - ids_asistentes_validos:
            self.add_error('asistencia_unidades', 'La lista incluye voluntarios inactivos o fuera de tu compañía.')
        if tipo != 'llegada_cuartel' and 'asistentes' not in self.errors:
            data['asistentes'] = self.fields['asistentes'].queryset.filter(pk__in=asistentes_por_unidad)
            data['asistencia_unidades_limpia'] = {
                str(unidad.pk): asistencia_normalizada.get(str(unidad.pk), [])
                for unidad in unidades_ordenadas
            }
        if tipo == 'combustible_6_14' and len(unidades_ordenadas) > 1:
            self.add_error('unidades', 'Registra cada carga de combustible para un solo carro.')

        if tipo in TIPOS_EMERGENCIA:
            familia = data.get('familia_codigo')
            codigos_familia = {codigo for codigo, _label in CLAVES_POR_FAMILIA.get(familia, [])}
            if not familia:
                self.add_error('familia_codigo', 'Selecciona la familia de la clave.')
            if data.get('codigo') and data['codigo'] not in codigos_familia:
                self.add_error('codigo', 'La clave no corresponde a la familia seleccionada.')
        if data.get('codigo') == 'otro' and not data.get('detalle_codigo', '').strip():
            self.add_error('detalle_codigo', 'Describe el tipo seleccionado como “Otro”.')

        if tipo == 'llegada_cuartel':
            if not data.get('fecha_inicio'):
                self.add_error('fecha_inicio', 'Ingresa la fecha de la emergencia.')
            if not data.get('direccion'):
                self.add_error('direccion', 'Ingresa la dirección de la emergencia.')
            if not data.get('emergencia_activa'):
                self.add_error('emergencia_activa', 'Selecciona una emergencia activa para vincular la asistencia.')
        elif tipo == 'ronda_maquinistas':
            if not data.get('vehiculo'):
                self.add_error('vehiculo', 'Selecciona la unidad que se revisó.')
            if not data.get('maquinista'):
                self.add_error('maquinista', 'Selecciona al conductor que realizó la ronda.')
            if data.get('fecha_inicio') is None:
                data['fecha_inicio'] = timezone.localdate()
        else:
            if not data.get('fecha_inicio'):
                self.add_error('fecha_inicio', 'La fecha de inicio es obligatoria.')
            es_combustible = tipo == 'combustible_6_14'
            if not es_combustible and not data.get('fecha_termino'):
                self.add_error('fecha_termino', 'La fecha de término/llegada es obligatoria.')
            if data.get('fecha_inicio') and data.get('fecha_termino') and data['fecha_termino'] < data['fecha_inicio']:
                self.add_error('fecha_termino', 'La fecha de término no puede ser anterior al inicio.')
            campos_requeridos = [('hora_despacho', 'la hora'), ('kilometraje_despacho', 'el kilometraje'), ('vehiculo', 'el carro')]
            if not es_combustible:
                campos_requeridos.extend([
                    ('hora_llegada', 'la hora de llegada'),
                    ('kilometraje_llegada', 'el kilometraje de llegada'),
                ])
            for field_name, label in campos_requeridos:
                if not data.get(field_name):
                    self.add_error(field_name, f'{label.capitalize()} es obligatorio.')
            if not es_combustible and data.get('kilometraje_despacho') is not None and data.get('kilometraje_llegada') is not None and data['kilometraje_llegada'] < data['kilometraje_despacho']:
                self.add_error('kilometraje_llegada', 'El kilometraje de llegada debe ser igual o mayor al de despacho.')
            if not es_combustible and data.get('fecha_inicio') and data.get('fecha_termino') and data.get('hora_despacho') and data.get('hora_llegada'):
                inicio = (data['fecha_inicio'], data['hora_despacho'])
                termino = (data['fecha_termino'], data['hora_llegada'])
                if termino <= inicio:
                    self.add_error('hora_llegada', 'La hora de llegada debe ser posterior al despacho; usa la fecha de llegada si cruzó medianoche.')
            if not data.get('direccion') and tipo != 'combustible_6_14':
                self.add_error('direccion', 'La dirección es obligatoria.')
            if tipo != 'practica_maquinista' and not data.get('maquinista'):
                self.add_error('maquinista', 'Selecciona el maquinista responsable.')
            if tipo in TIPOS_EMERGENCIA and not data.get('codigo'):
                self.add_error('codigo', 'Selecciona el código de la emergencia.')
            if tipo == 'servicio_especial' and not data.get('codigo'):
                self.add_error('codigo', 'Selecciona el tipo de servicio especial.')
            if tipo in {'emergencia', 'emergencia_vehicular', 'servicio_especial', 'rodaje', 'se_dirige_6_13', 'rodaje_6_13'} and not data.get('obac_voluntario'):
                self.add_error('obac_voluntario', 'Selecciona el OBAC responsable.')
            if tipo == 'emergencia_vehicular':
                apoyos_validos = {'municipalidad', 'carabineros', 'ambulancia', 'ruta_5_sur', 'otro_cuerpo', 'otros'}
                if set(data.get('instituciones_apoyo') or []) - apoyos_validos:
                    self.add_error('instituciones_apoyo', 'Selecciona solo apoyos disponibles para emergencias vehiculares.')
                if not data.get('informe'):
                    self.add_error('informe', 'El informe de la emergencia vehicular es obligatorio.')
                if not data.get('lesionados_externos'):
                    self.add_error('lesionados_externos', 'Indica los lesionados externos o escribe “Sin lesionados”.')
            if tipo in TIPOS_CON_NOVEDADES and not data.get('novedades_unidad'):
                self.add_error('novedades_unidad', 'Describe las novedades o escribe “Sin novedad”.')
            if tipo in {'servicio_especial', 'practica_maquinista'} and not data.get('autorizado_por'):
                self.add_error('autorizado_por', 'Selecciona quién autorizó la actividad.')
            apoyos = set(data.get('instituciones_apoyo') or [])
            if 'otro_cuerpo' in apoyos and not data.get('apoyo_otro_cuerpo'):
                self.add_error('apoyo_otro_cuerpo', 'Indica el nombre del Cuerpo de Bomberos.')
            if 'otros' in apoyos and not data.get('apoyo_otros'):
                self.add_error('apoyo_otros', 'Describe la institución de apoyo.')
            if tipo == 'servicio_especial' and not data.get('informe'):
                self.add_error('informe', 'Describe la actividad especial realizada.')
            if tipo in {'rodaje', 'se_dirige_6_13', 'rodaje_6_13'} and not data.get('informe'):
                self.add_error('informe', 'Describe brevemente el recorrido o prueba realizada.')
            if tipo == 'combustible_6_14':
                if not data.get('estacion_servicio'):
                    self.add_error('estacion_servicio', 'Selecciona la estación de servicio.')
                if data.get('estacion_servicio') == 'otra' and not data.get('estacion_detalle'):
                    self.add_error('estacion_detalle', 'Especifica la estación de servicio.')
                if not data.get('combustible_tipo'):
                    self.add_error('combustible_tipo', 'Selecciona el tipo de combustible.')
                if not data.get('monto_combustible') or data.get('monto_combustible') <= 0:
                    self.add_error('monto_combustible', 'El monto cargado debe ser mayor que cero.')
            if tipo == 'practica_maquinista' and not data.get('instructor'):
                self.add_error('instructor', 'Selecciona el instructor.')

        if 'involucrados_json' in self.cleaned_data:
            involucrados = self._json_list('involucrados_json', 'involucrados')
            for persona in involucrados:
                if not isinstance(persona, dict) or any(not str(persona.get(key, '')).strip() for key in ('nombre', 'rut', 'tipo_vehiculo', 'patente')):
                    raise ValidationError('Completa nombre, RUT, tipo de vehículo y patente en cada involucrado.')
            self.instance.involucrados = involucrados

        if 'checklist_json' in self.cleaned_data:
            checklist = self._json_list('checklist_json', 'checklist')
            if tipo == 'ronda_maquinistas':
                by_id = {item.get('id'): item for item in checklist if isinstance(item, dict)}
                for item_id, label, choices in RONDAS_CHECKLIST:
                    item = by_id.get(item_id)
                    if not item or item.get('respuesta') not in choices:
                        self.add_error('checklist_json', f'Revisa el ítem obligatorio: {label}.')
                    elif self._es_hallazgo(item.get('respuesta')) and not str(item.get('observacion', '')).strip():
                        self.add_error('checklist_json', f'Describe el problema detectado en: {label}.')
            self.instance.checklist = checklist

        if self.instance.tipo == 'llegada_cuartel':
            emergencia = data.get('emergencia_activa')
            if emergencia:
                self.instance.emergencia = emergencia
                self.instance.codigo = emergencia.tipo
        return data

    @staticmethod
    def _es_hallazgo(respuesta):
        return respuesta in {'No', 'En mal estado', 'Bajo aceite motor', 'Bajo refrigerante'}


def _momento(fecha, hora):
    value = datetime.combine(fecha, hora)
    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.get_current_timezone())
    return value


def _puede_registrar(user, tipo):
    rol = getattr(user, 'rol', None)
    if tipo in TIPOS_EMERGENCIA or tipo == 'llegada_cuartel':
        return user.is_superuser or bool(rol and rol.editar_emergencias)
    return user.is_superuser or bool(rol and rol.editar_salidas_terreno)


def _guardar_registro(form, user):
    tipo = form.cleaned_data['tipo']
    registro = form.save(commit=False)
    registro.creado_por = user
    unidades = list(form.cleaned_data.get('unidades') or [])
    asistencia_unidades = form.cleaned_data.get('asistencia_unidades_limpia', {})
    if tipo == 'llegada_cuartel':
        registro.emergencia = form.cleaned_data['emergencia_activa']
        registro.codigo = registro.emergencia.tipo

    with transaction.atomic():
        if tipo == 'combustible_6_14':
            compania = registro.vehiculo.compania
            movimientos = CajaChica.objects.select_for_update().filter(compania=compania, tipo_cuenta='caja_propia')
            saldo = sum((monto if movimiento_tipo == 'Ingreso' else -monto for movimiento_tipo, monto in movimientos.values_list('tipo', 'monto')), Decimal('0'))
            if saldo < registro.monto_combustible:
                raise ValidationError(f'La Caja propia de {compania.nombre} no tiene saldo suficiente. Saldo disponible: ${saldo:,.0f}.')
            momento_caja = _momento(registro.fecha_inicio, registro.hora_despacho or datetime.min.time())
            caja = CajaChica.objects.create(
                fecha=momento_caja,
                tipo='Egreso',
                tipo_cuenta='caja_propia',
                monto=registro.monto_combustible,
                descripcion=(
                    f'Combustible {registro.get_combustible_tipo_display()} — {registro.vehiculo.nombre} — '
                    f'{registro.estacion_detalle if registro.estacion_servicio == "otra" else registro.get_estacion_servicio_display()} — '
                    f'Maquinista: {registro.maquinista.get_full_name()}'
                )[:255],
                responsable=registro.maquinista,
                compania=compania,
            )
            registro.movimiento_caja = caja

        registro.save()
        form.save_m2m()

        for unidad in unidades:
            detalle_registro, _ = RegistroOperativoUnidad.objects.get_or_create(
                registro=registro,
                unidad=unidad,
            )
            detalle_registro.asistentes.set(asistencia_unidades.get(str(unidad.pk), []))

        if tipo in TIPOS_EMERGENCIA:
            alarma = _momento(registro.fecha_inicio, registro.hora_despacho)
            nombres_unidades = ', '.join(unidad.nombre for unidad in unidades)
            emergencia = Emergencia.objects.create(
                tipo=registro.codigo,
                direccion=registro.direccion,
                fecha_hora_alarma=alarma,
                descripcion='\n'.join(filter(None, [registro.informe, f'OBAC: {registro.obac}', f'Apoyos: {", ".join(registro.instituciones_apoyo)}', registro.novedades_unidad])),
                unidades_despachadas=nombres_unidades[:100],
                estado='Finalizada',
                creado_por=user,
                registro_completado=True,
            )
            # Emergencia stores dispatched vehicles and per-vehicle attendance
            # through EmergenciaUnidad (it has no direct unidades M2M field).
            emergencia.asistentes.set(registro.asistentes.all())
            for unidad in unidades:
                detalle = EmergenciaUnidad.objects.create(emergencia=emergencia, unidad=unidad)
                detalle.asistentes.set(asistencia_unidades.get(str(unidad.pk), []))
            registro.emergencia = emergencia
            registro.save(update_fields=['emergencia'])
        elif tipo == 'llegada_cuartel':
            registro.emergencia.asistentes.add(*registro.asistentes.all())
        elif tipo == 'ronda_maquinistas':
            hallazgos = []
            checklist_by_id = {item['id']: item for item in registro.checklist}
            for item_id, label, _choices in RONDAS_CHECKLIST:
                item = checklist_by_id[item_id]
                respuesta = item['respuesta']
                detalle_texto = str(item.get('observacion', '')).strip()
                if RegistroOperativoForm._es_hallazgo(respuesta):
                    hallazgos.append((label, respuesta, detalle_texto))
            for unidad in unidades:
                for label, respuesta, detalle_texto in hallazgos:
                    RondaVehiculo.objects.create(
                        vehiculo=unidad,
                        registrado_por=registro.maquinista,
                        tipo_hallazgo='Falla',
                        detalle=f'{label}: {respuesta}. {detalle_texto}',
                    )
                if not hallazgos:
                    RondaVehiculo.objects.create(
                        vehiculo=unidad,
                        registrado_por=registro.maquinista,
                        tipo_hallazgo='Sin novedad',
                        detalle='Ronda preventiva completada sin novedades.',
                    )
        else:
            inicio = _momento(registro.fecha_inicio, registro.hora_despacho)
            fin = None if tipo == 'combustible_6_14' else _momento(registro.fecha_termino or registro.fecha_inicio, registro.hora_llegada)
            motivo = f'{registro.get_tipo_display()} — {registro.codigo or registro.get_tipo_display()}'
            autorizaciones = ', '.join(usuario.nombre_operativo for usuario in registro.autorizado_por.all())
            descripcion = '\n'.join(filter(None, [registro.informe, f'OBAC: {registro.obac}', f'Autorizado por: {autorizaciones}', registro.novedades_unidad]))
            salida = SalidaTerreno.objects.create(
                motivo=motivo[:255],
                direccion=registro.estacion_detalle if tipo == 'combustible_6_14' and registro.estacion_servicio == 'otra' else (registro.get_estacion_servicio_display() if tipo == 'combustible_6_14' else registro.direccion),
                fecha_hora_salida=inicio,
                fecha_hora_regreso=fin,
                unidades_involucradas=', '.join(unidad.nombre for unidad in unidades)[:200],
                kilometraje_salida=registro.kilometraje_despacho or 0,
                kilometraje_regreso=registro.kilometraje_llegada,
                personal_a_cargo=registro.maquinista,
                descripcion=descripcion,
                creado_por=user,
            )
            salida.unidades.set(unidades)
            for unidad in unidades:
                detalle = SalidaTerrenoUnidad.objects.create(salida=salida, unidad=unidad)
                detalle.asistentes.set(asistencia_unidades.get(str(unidad.pk), []))
            registro.salida_terreno = salida
            registro.save(update_fields=['salida_terreno'])

        kilometraje_actual = registro.kilometraje_despacho if tipo == 'combustible_6_14' else registro.kilometraje_llegada
        if registro.vehiculo and kilometraje_actual is not None:
            if registro.vehiculo.odometro_actual is None or kilometraje_actual >= registro.vehiculo.odometro_actual:
                registro.vehiculo.odometro_actual = kilometraje_actual
                registro.vehiculo.save(update_fields=['odometro_actual'])

        if tipo in TIPOS_CON_NOVEDADES and registro.novedades_unidad.strip().casefold() not in {'sin novedad', 'sin novedades', 'ninguna'}:
            for unidad in unidades:
                RondaVehiculo.objects.create(
                    vehiculo=unidad,
                    registrado_por=registro.maquinista,
                    tipo_hallazgo='Observación',
                    detalle=f'{registro.get_tipo_display()} ({registro.fecha_inicio:%d/%m/%Y}): {registro.novedades_unidad}',
                )
    return registro


@login_required
def registro_operativo_view(request):
    rol = getattr(request.user, 'rol', None)
    puede_ver = request.user.is_superuser or bool(rol and (rol.ver_emergencias or rol.ver_salidas_terreno))
    if not puede_ver:
        messages.error(request, 'No tienes permiso para acceder a los registros operativos.')
        return redirect('dashboard')
    puede_registrar_emergencias = request.user.is_superuser or bool(rol and rol.editar_emergencias)
    puede_registrar_salidas = request.user.is_superuser or bool(rol and rol.editar_salidas_terreno)
    if not (puede_registrar_emergencias or puede_registrar_salidas):
        messages.error(request, 'No tienes permiso para registrar actividades operativas.')
        return redirect('emergencias')

    form = RegistroOperativoForm(request.POST or None, user=request.user)
    if request.method == 'POST':
        tipo = request.POST.get('tipo', '')
        if not _puede_registrar(request.user, tipo):
            messages.error(request, 'No tienes permiso para registrar este tipo de actividad.')
        elif form.is_valid():
            try:
                registro = _guardar_registro(form, request.user)
            except ValidationError as error:
                form.add_error(None, error.message)
            else:
                messages.success(request, f'{registro.get_tipo_display()} registrado correctamente.')
                return redirect(reverse('registro_operativo'))

    registros = RegistroOperativo.objects.select_related(
        'vehiculo', 'maquinista', 'creado_por', 'emergencia', 'salida_terreno'
    ).prefetch_related('asistentes', 'unidades')

    tipos_emergencia = TIPOS_EMERGENCIA | {'llegada_cuartel'}
    tipos_visibles = []
    if request.user.is_superuser or (rol and rol.ver_emergencias):
        tipos_visibles.extend(tipos_emergencia)
    if request.user.is_superuser or (rol and rol.ver_salidas_terreno):
        tipos_visibles.extend(
            tipo for tipo, _etiqueta in RegistroOperativo.TIPO_CHOICES
            if tipo not in tipos_emergencia
        )
    registros = registros.filter(tipo__in=tipos_visibles)

    rol_nombre = getattr(rol, 'nombre', '').strip().casefold()
    puede_ver_todas_companias = request.user.is_superuser or rol_nombre in {'admin', 'administrador'}
    if not puede_ver_todas_companias:
        if request.user.compania_id:
            compania_id = request.user.compania_id
            registros = registros.filter(
                Q(vehiculo__compania_id=compania_id)
                | Q(unidades__compania_id=compania_id)
                | Q(emergencia__unidades_asistencia__unidad__compania_id=compania_id)
                | Q(salida_terreno__unidades__compania_id=compania_id)
            ).distinct()
        else:
            registros = registros.none()

    registros = registros.order_by('-fecha_inicio', '-creado_en')[:30]
    unidades_iniciales = request.POST.getlist('unidades') if request.method == 'POST' else []
    if request.method != 'POST' and request.GET.get('vehiculo'):
        unidades_iniciales = [request.GET.get('vehiculo')]
    if request.method == 'POST' and not unidades_iniciales and request.POST.get('vehiculo'):
        unidades_iniciales = [request.POST.get('vehiculo')]
    usuarios_asistencia = [
        {'id': voluntario.pk, 'nombre': voluntario.nombre_operativo}
        for voluntario in form.fields['asistentes'].queryset
    ]
    return render(request, 'usuarios/registro_operativo.html', {
        'form': form,
        'registros': registros,
        'rondas_checklist': RONDAS_CHECKLIST,
        'codigos_por_tipo': RegistroOperativoForm.CODIGOS,
        'claves_por_familia': CLAVES_POR_FAMILIA,
        'familias_claves': FAMILIAS_CLAVES_EMERGENCIA,
        'puede_registrar_emergencias': puede_registrar_emergencias,
        'puede_registrar_salidas': puede_registrar_salidas,
        'unidades_iniciales': unidades_iniciales,
        'usuarios_asistencia': usuarios_asistencia,
    })
