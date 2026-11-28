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
    'practica_maquinista', 'rodaje_6_13', 'combustible_6_14',
}
TIPOS_CON_NOVEDADES = {
    'emergencia', 'emergencia_vehicular', 'servicio_especial',
    'practica_maquinista', 'rodaje_6_13',
}


class RegistroOperativoForm(forms.ModelForm):
    codigo = forms.ChoiceField(label='Código / tipo', choices=(), required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    instituciones_apoyo = forms.MultipleChoiceField(
        label='Apoyo de otras instituciones', choices=RegistroOperativo.APOYO_CHOICES,
        required=False, widget=forms.CheckboxSelectMultiple,
    )
    autorizaciones = forms.MultipleChoiceField(
        label='Autorizado por', choices=[('6', '6'), ('7', '7'), ('1', '1'), ('2', '2')],
        required=False, widget=forms.CheckboxSelectMultiple,
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

    class Meta:
        model = RegistroOperativo
        fields = [
            'tipo', 'codigo', 'fecha_inicio', 'fecha_termino', 'hora_despacho', 'hora_llegada',
            'kilometraje_despacho', 'kilometraje_llegada', 'direccion', 'estacion_servicio',
            'estacion_detalle', 'vehiculo', 'maquinista', 'obac', 'apoyo_otro_cuerpo',
            'instituciones_apoyo', 'apoyo_otros', 'informe', 'novedades_unidad', 'lesionados_externos',
            'aspirante_nombre', 'aspirante_clave', 'instructor', 'combustible_tipo',
            'monto_combustible', 'autorizaciones', 'asistentes',
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
            'vehiculo': forms.Select(attrs={'class': 'form-select'}),
            'maquinista': forms.Select(attrs={'class': 'form-select'}),
            'obac': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del oficial o voluntario'}),
            'apoyo_otro_cuerpo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Cuerpo de Bomberos'}),
            'apoyo_otros': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especifica la institución'}),
            'informe': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'novedades_unidad': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Indica las novedades o “Sin novedad”'}),
            'lesionados_externos': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Nombre y RUT'}),
            'aspirante_nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'aspirante_clave': forms.TextInput(attrs={'class': 'form-control'}),
            'instructor': forms.Select(attrs={'class': 'form-select'}),
            'combustible_tipo': forms.Select(attrs={'class': 'form-select'}),
            'monto_combustible': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '1', 'inputmode': 'decimal'}),
        }

    CODIGOS = {
        'emergencia': [
            ('10-0-1', '10-0-1 — Incendio estructural'),
            ('10-0-15', '10-0-15 — Incendio rural'),
            ('10-0-7', '10-0-7 — Inflamación de ducto'),
            ('10-1-1', '10-1-1 — Incendio vehicular menor'),
            ('10-1-2', '10-1-2 — Incendio de camión'),
            ('10-1-5', '10-1-5 — Incendio de maquinaria forestal'),
            ('10-2-1', '10-2-1 — Incendio de pastizal urbano'),
            ('10-2-2', '10-2-2 — Incendio de pastizal rural'),
            ('10-2-3', '10-2-3 — Incendio agrícola'),
            ('10-2-4', '10-2-4 — Incendio de microbasural'),
            ('10-3', '10-3 — Rescate de persona'),
            ('10-4', '10-4 — Rescate vehicular'),
            ('10-6', '10-6 — Emanación de gas'),
            ('10-7', '10-7 — Riesgo eléctrico'),
            ('10-8', '10-8 — Llamado no clasificado'),
            ('10-8-8', '10-8-8 — Rastreo de persona'),
            ('10-8-10', '10-8-10 — Rastreo en aguas abiertas'),
            ('10-8-11', '10-8-11 — Recuperación de cadáver'),
            ('10-8-13', '10-8-13 — Caída de árbol'),
            ('10-8-14', '10-8-14 — Voladuras de techo'),
            ('10-8-15', '10-8-15 — Inundación'),
            ('10-8-16', '10-8-16 — Rescate de animal'),
            ('10-8-18', '10-8-18 — Derrame'),
            ('10-9-7', '10-9-7 — Inspección'),
            ('9-3', '9-3 — Acuartelamiento general'),
            ('10-12', '10-12 — Apoyo a otro Cuerpo'),
            ('10-10', '10-10 — Rebrote de fuego'),
            ('9-4', '9-4 — Acuartelamiento preventivo'),
            ('otro', 'Otro'),
        ],
        'emergencia_vehicular': [('10-4', '10-4 — Rescate vehicular')],
        'servicio_especial': [
            ('reunion_superintendencia', 'Reunión de Superintendencia'),
            ('reunion_comandancia', 'Reunión de Comandancia'),
            ('actividad_entidad', 'Actividad solicitada por otra entidad'),
            ('simulacro', 'Simulacro'), ('otro', 'Otro'),
        ],
        'practica_maquinista': [('practica_maquinista', 'Práctica de maquinista')],
        'rodaje_6_13': [('6-13', '6-13 — Se dirige a')],
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
            if (choice[0] in TIPOS_EMERGENCIA or choice[0] == 'llegada_cuartel') and puede_emergencias
            or (choice[0] not in TIPOS_EMERGENCIA and choice[0] != 'llegada_cuartel') and puede_salidas
        ]
        self.fields['tipo'].choices = tipos_disponibles
        if tipos_disponibles and not self.is_bound:
            self.fields['tipo'].initial = tipos_disponibles[0][0]
        tipo = (self.data.get('tipo') if self.is_bound else self.initial.get('tipo')) or 'emergencia'
        codigos = list(self.CODIGOS.get(tipo, []))
        codigo_actual = getattr(self.instance, 'codigo', '')
        if self.instance.pk and codigo_actual and all(valor != codigo_actual for valor, _ in codigos):
            codigos.append((codigo_actual, f'{codigo_actual} — Código histórico'))
        self.fields['codigo'].choices = [('', 'Seleccionar')] + codigos
        self.fields['vehiculo'].queryset = Vehiculo.objects.select_related('compania').order_by('compania__nombre', 'nombre')
        self.fields['maquinista'].queryset = Usuario.objects.miembros_activos().order_by('nombre', 'apellido')
        self.fields['instructor'].queryset = Usuario.objects.miembros_activos().order_by('nombre', 'apellido')
        self.fields['asistentes'].queryset = Usuario.objects.miembros_activos().order_by('nombre', 'apellido')
        if user and not user.is_superuser and user.compania_id and getattr(getattr(user, 'rol', None), 'nombre', '').strip().casefold() not in {'admin', 'administrador'}:
            self.fields['vehiculo'].queryset = self.fields['vehiculo'].queryset.filter(compania_id=user.compania_id)
            self.fields['maquinista'].queryset = self.fields['maquinista'].queryset.filter(compania_id=user.compania_id)
            self.fields['instructor'].queryset = self.fields['instructor'].queryset.filter(compania_id=user.compania_id)
            self.fields['asistentes'].queryset = self.fields['asistentes'].queryset.filter(compania_id=user.compania_id)
        self.fields['vehiculo'].empty_label = 'Seleccionar carro'
        self.fields['maquinista'].empty_label = 'Seleccionar maquinista'
        self.fields['instructor'].empty_label = 'Seleccionar instructor'
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
        self.fields['estacion_detalle'].required = False

    def clean_instituciones_apoyo(self):
        return list(self.cleaned_data.get('instituciones_apoyo') or [])

    def clean_autorizaciones(self):
        values = list(self.cleaned_data.get('autorizaciones') or [])
        tipo = self.data.get('tipo') or self.initial.get('tipo') or ''
        permitidos = {'6', '1', '2'} if tipo == 'servicio_especial' else {'6', '7', '1', '2'}
        if set(values) - permitidos:
            raise ValidationError('La autorización seleccionada no corresponde a este tipo de actividad.')
        return values

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
            if not data.get('direccion') and tipo != 'combustible_6_14':
                self.add_error('direccion', 'La dirección es obligatoria.')
            if tipo != 'practica_maquinista' and not data.get('maquinista'):
                self.add_error('maquinista', 'Selecciona el maquinista responsable.')
            if tipo in TIPOS_EMERGENCIA and not data.get('codigo'):
                self.add_error('codigo', 'Selecciona el código de la emergencia.')
            if tipo == 'servicio_especial' and not data.get('codigo'):
                self.add_error('codigo', 'Selecciona el tipo de servicio especial.')
            if tipo in {'emergencia', 'emergencia_vehicular', 'servicio_especial', 'rodaje_6_13'} and not data.get('obac'):
                self.add_error('obac', 'Indica el OBAC responsable.')
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
            if tipo in {'servicio_especial', 'practica_maquinista'} and not data.get('autorizaciones'):
                self.add_error('autorizaciones', 'Selecciona quién autorizó la actividad.')
            apoyos = set(data.get('instituciones_apoyo') or [])
            if 'otro_cuerpo' in apoyos and not data.get('apoyo_otro_cuerpo'):
                self.add_error('apoyo_otro_cuerpo', 'Indica el nombre del Cuerpo de Bomberos.')
            if 'otros' in apoyos and not data.get('apoyo_otros'):
                self.add_error('apoyo_otros', 'Describe la institución de apoyo.')
            if tipo == 'servicio_especial' and not data.get('informe'):
                self.add_error('informe', 'Describe la actividad especial realizada.')
            if tipo == 'rodaje_6_13' and not data.get('informe'):
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

        if tipo in TIPOS_EMERGENCIA:
            alarma = _momento(registro.fecha_inicio, registro.hora_despacho)
            emergencia = Emergencia.objects.create(
                tipo=registro.codigo,
                direccion=registro.direccion,
                fecha_hora_alarma=alarma,
                descripcion='\n'.join(filter(None, [registro.informe, f'OBAC: {registro.obac}', f'Apoyos: {", ".join(registro.instituciones_apoyo)}', registro.novedades_unidad])),
                unidades_despachadas=registro.vehiculo.nombre,
                estado='Finalizada',
                creado_por=user,
                registro_completado=True,
            )
            detalle = EmergenciaUnidad.objects.create(emergencia=emergencia, unidad=registro.vehiculo)
            detalle.asistentes.set(registro.asistentes.all())
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
                    hallazgos.append(f'{label}: {respuesta}. {detalle_texto}')
                    RondaVehiculo.objects.create(
                        vehiculo=registro.vehiculo,
                        registrado_por=registro.maquinista,
                        tipo_hallazgo='Falla',
                        detalle=f'{label}: {respuesta}. {detalle_texto}',
                    )
            if not hallazgos:
                RondaVehiculo.objects.create(
                    vehiculo=registro.vehiculo,
                    registrado_por=registro.maquinista,
                    tipo_hallazgo='Sin novedad',
                    detalle='Ronda preventiva completada sin novedades.',
                )
        else:
            inicio = _momento(registro.fecha_inicio, registro.hora_despacho)
            fin = None if tipo == 'combustible_6_14' else _momento(registro.fecha_termino or registro.fecha_inicio, registro.hora_llegada)
            motivo = f'{registro.get_tipo_display()} — {registro.codigo or registro.get_tipo_display()}'
            descripcion = '\n'.join(filter(None, [registro.informe, f'OBAC: {registro.obac}', f'Autorizado por: {", ".join(registro.autorizaciones)}', registro.novedades_unidad]))
            salida = SalidaTerreno.objects.create(
                motivo=motivo[:255],
                direccion=registro.estacion_detalle if tipo == 'combustible_6_14' and registro.estacion_servicio == 'otra' else (registro.get_estacion_servicio_display() if tipo == 'combustible_6_14' else registro.direccion),
                fecha_hora_salida=inicio,
                fecha_hora_regreso=fin,
                unidades_involucradas=registro.vehiculo.nombre,
                kilometraje_salida=registro.kilometraje_despacho or 0,
                kilometraje_regreso=registro.kilometraje_llegada,
                personal_a_cargo=registro.maquinista,
                descripcion=descripcion,
                creado_por=user,
            )
            salida.unidades.set([registro.vehiculo])
            detalle = SalidaTerrenoUnidad.objects.create(salida=salida, unidad=registro.vehiculo)
            detalle.asistentes.set(registro.asistentes.all())
            registro.salida_terreno = salida
            registro.save(update_fields=['salida_terreno'])

        kilometraje_actual = registro.kilometraje_despacho if tipo == 'combustible_6_14' else registro.kilometraje_llegada
        if registro.vehiculo and kilometraje_actual is not None:
            if registro.vehiculo.odometro_actual is None or kilometraje_actual >= registro.vehiculo.odometro_actual:
                registro.vehiculo.odometro_actual = kilometraje_actual
                registro.vehiculo.save(update_fields=['odometro_actual'])

        if tipo in TIPOS_CON_NOVEDADES and registro.novedades_unidad.strip().casefold() not in {'sin novedad', 'sin novedades', 'ninguna'}:
            RondaVehiculo.objects.create(
                vehiculo=registro.vehiculo,
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
    ).prefetch_related('asistentes')

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
                | Q(emergencia__unidades_asistencia__unidad__compania_id=compania_id)
                | Q(salida_terreno__unidades__compania_id=compania_id)
            ).distinct()
        else:
            registros = registros.none()

    registros = registros.order_by('-fecha_inicio', '-creado_en')[:30]
    return render(request, 'usuarios/registro_operativo.html', {
        'form': form,
        'registros': registros,
        'rondas_checklist': RONDAS_CHECKLIST,
        'codigos_por_tipo': RegistroOperativoForm.CODIGOS,
        'puede_registrar_emergencias': puede_registrar_emergencias,
        'puede_registrar_salidas': puede_registrar_salidas,
    })
