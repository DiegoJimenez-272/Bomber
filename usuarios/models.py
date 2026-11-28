from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
import qrcode
from io import BytesIO
from django.core.files import File
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime
from django.utils import timezone
from .validators import validar_extension_archivo, validar_extension_imagen, validar_documento_vehiculo, SecureFilePath, validar_rut_chileno

class Rol(models.Model):

    nombre = models.CharField(max_length=80)
    descripcion = models.TextField(max_length=1200)
    
    # --- Permisos de Acceso a Módulos ---
    ver_resumen_general = models.BooleanField(default=False, verbose_name="Resumen General")
    ver_estadisticas_operativas = models.BooleanField(default=False, verbose_name="Estadísticas Operativas")
    ver_documentacion = models.BooleanField(default=False, verbose_name="Documentación")
    ver_escanear_qr = models.BooleanField(default=False, verbose_name="Escanear QR")
    ver_inventario = models.BooleanField(default=False, verbose_name="Inventario")
    ver_salidas_terreno = models.BooleanField(default=False, verbose_name="Salidas a terreno")
    ver_emergencias = models.BooleanField(default=False, verbose_name="Emergencias")
    ver_capacitaciones = models.BooleanField(default=False, verbose_name="Cursos")
    ver_malla_curricular = models.BooleanField(default=False, verbose_name="Malla Curricular")
    ver_mantenimientos = models.BooleanField(default=False, verbose_name="Mantenimientos")
    ver_proyectos = models.BooleanField(default=False, verbose_name="Proyectos")
    ver_caja_chica = models.BooleanField(default=False, verbose_name="Caja Chica")
    ver_avisos = models.BooleanField(default=False, verbose_name="Avisos")
    ver_inspectores = models.BooleanField(default=False, verbose_name="Inspectores")
    ver_novedades = models.BooleanField(default=False, verbose_name="Novedades")

    # --- Permisos de Edición / Creación / Eliminación ---
    editar_documentacion = models.BooleanField(default=False, verbose_name="Editar Documentación")
    editar_inventario = models.BooleanField(default=False, verbose_name="Editar Inventario")
    gestionar_inventario_todas_companias = models.BooleanField(
        default=False,
        verbose_name="Gestionar inventario de todas las compañías",
        help_text="Permite al rol administrar inventario y vehículos de cualquier compañía.",
    )
    editar_salidas_terreno = models.BooleanField(default=False, verbose_name="Editar Salidas a terreno")
    editar_emergencias = models.BooleanField(default=False, verbose_name="Editar Emergencias")
    editar_capacitaciones = models.BooleanField(default=False, verbose_name="Editar Cursos")
    editar_malla_curricular = models.BooleanField(default=False, verbose_name="Editar Malla Curricular")
    editar_mantenimientos = models.BooleanField(default=False, verbose_name="Editar Mantenimientos")
    editar_proyectos = models.BooleanField(default=False, verbose_name="Editar Proyectos")
    editar_caja_chica = models.BooleanField(default=False, verbose_name="Editar Caja Chica")
    editar_avisos = models.BooleanField(default=False, verbose_name="Editar Avisos")
    editar_inspectores = models.BooleanField(default=False, verbose_name="Editar Inspectores")
    editar_novedades = models.BooleanField(default=False, verbose_name="Editar Novedades")

    def __str__(self):
        return self.nombre

class Compania(models.Model):
    nombre = models.CharField(max_length=80)
    ubicacion = models.CharField(max_length=80)
    logo = models.ImageField(upload_to=SecureFilePath('logos_companias/'), null=True, blank=True, verbose_name='Logo de la Compañía', validators=[validar_extension_imagen])
    
    def __str__(self):
        return self.nombre 

class EspecialidadVoluntario(models.Model):
    slug = models.SlugField(max_length=50, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    activa = models.BooleanField(default=True)
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['orden', 'nombre']
        verbose_name = 'Especialidad de voluntario'
        verbose_name_plural = 'Especialidades de voluntarios'

    def __str__(self):
        return self.nombre

class UsuarioManager(BaseUserManager):
    def miembros_activos(self):
        return self.filter(is_active=True, compania__isnull=False)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    nombre = models.CharField(max_length=80)
    apellido = models.CharField(max_length=80)
    email = models.EmailField(unique=True, max_length=80)
    rut = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name='RUT', validators=[validar_rut_chileno])
    clave_radial = models.CharField(max_length=20, null=True, blank=True, verbose_name='Clave Radial')
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
    compania = models.ForeignKey(Compania, on_delete=models.SET_NULL, null=True, blank=True)
    especialidades = models.ManyToManyField(
        'EspecialidadVoluntario', blank=True, related_name='voluntarios',
        verbose_name='Especialidades operativas',
    )
    foto_perfil = models.ImageField(upload_to=SecureFilePath('fotos_perfil/'), null=True, blank=True, verbose_name='Foto de Perfil', validators=[validar_extension_imagen])
    
    # Campos requeridos para AbstractBaseUser
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido', 'rut']
    
    def __str__(self):
        return self.nombre_operativo
    
    def get_full_name(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def nombre_operativo(self):
        """Identifica al voluntario en listas operativas sin exponer su correo."""
        nombre = self.get_full_name().strip().title()
        clave = (self.clave_radial or '').strip() or '—'
        return f'{clave} · {nombre}' if nombre else clave
    
    def get_short_name(self):
        return self.nombre

    @property
    def es_inspector(self):
        rol = self.rol
        return bool(rol and (rol.nombre or '').strip().casefold() == 'inspector')

    @property
    def es_programador(self):
        return (self.clave_radial or '').strip().casefold() == 'programador'

    def save(self, *args, **kwargs):
        if self.pk:
            try:
                old_usuario = Usuario.objects.get(pk=self.pk)
                if old_usuario.compania != self.compania:
                    # La compañía cambió, desasignar equipos de la compañía anterior
                    items_a_desasignar = self.inventario_asignado.filter(compania=old_usuario.compania)
                    for item in items_a_desasignar:
                        item_name = item.get_nombre_display()
                        item.asignado_a = None
                        item.save() # El método save de Inventario limpiará automáticamente el código QR
                        Notificacion.objects.create(
                            usuario=self,
                            mensaje=f"El equipo {item_name} fue devuelto a bodega por cambio de compañía.",
                            link="/inventario/"
                        )
            except Usuario.DoesNotExist:
                pass
        super().save(*args, **kwargs)

class Proyecto(models.Model):
    TIPO_PROYECTO_CHOICES = [
        ('Infraestructura', 'Infraestructura'),
        ('Equipamiento', 'Equipamiento'),
        ('Capacitación', 'Capacitación'),
        ('Otro', 'Otro'),
    ]

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    presupuesto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='proyectos_responsable')
    tipo = models.CharField(max_length=50, choices=TIPO_PROYECTO_CHOICES, default='Otro')
    prioridad = models.PositiveIntegerField(default=50)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='proyectos_creados')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class ArchivoProyecto(models.Model):
    proyecto = models.ForeignKey(Proyecto, related_name='archivos', on_delete=models.CASCADE)
    archivo = models.FileField(upload_to=SecureFilePath('proyectos_archivos/'), validators=[validar_extension_archivo])
    subido_en = models.DateTimeField(auto_now_add=True)

class Carpeta(models.Model):
    nombre = models.CharField(max_length=100)
    padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcarpetas')
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE, null=True, blank=True, related_name='carpetas')
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    es_privado = models.BooleanField(default=False)
    es_de_inspector = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

    class Meta:
        ordering = ['-creado_en']

class Documento(models.Model):
    TIPO_DOCUMENTO_CHOICES = [
        ('General', 'Documento General'),
        ('Orden del Día', 'Orden del Día'),
        ('Circular', 'Circular'),
        ('Formulario', 'Formulario'),
        ('Otro', 'Otro'),
    ]

    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to=SecureFilePath('documentos/'), validators=[validar_extension_archivo])
    tipo = models.CharField(max_length=50, choices=TIPO_DOCUMENTO_CHOICES, default='General')
    carpeta = models.ForeignKey(Carpeta, on_delete=models.CASCADE, null=True, blank=True, related_name='documentos')
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE, null=True, blank=True, related_name='documentos')
    subido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    subido_en = models.DateTimeField(auto_now_add=True)
    es_privado = models.BooleanField(default=False)
    es_de_inspector = models.BooleanField(default=False)
    vigente = models.BooleanField(default=True, verbose_name='Documento vigente')

    def __str__(self):
        return self.nombre

    @property
    def archivo_existe(self):
        """Comprueba si el archivo físico aún existe en el sistema de archivos."""
        if self.archivo:
            try:
                return self.archivo.storage.exists(self.archivo.name)
            except Exception:
                return False
        return False

    @property
    def extension_archivo(self):
        """Devuelve la extensión del archivo en minúsculas para la vista previa."""
        nombre = self.archivo.name if self.archivo else ''
        return nombre.rsplit('.', 1)[-1].lower() if '.' in nombre else ''

    @property
    def tamano_seguro(self):
        """Devuelve el tamaño del archivo de forma segura, o 0 si no existe."""
        if self.archivo_existe:
            return self.archivo.size
        return 0

class SalidaTerreno(models.Model):
    motivo = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    fecha_hora_salida = models.DateTimeField()
    fecha_hora_regreso = models.DateTimeField(null=True, blank=True)
    unidades_involucradas = models.CharField(max_length=200)
    unidades = models.ManyToManyField(
        'Vehiculo',
        blank=True,
        related_name='salidas_terreno',
        verbose_name="Unidades involucradas",
    )
    kilometraje_salida = models.PositiveIntegerField(verbose_name="Kilometraje de Salida")
    kilometraje_regreso = models.PositiveIntegerField(verbose_name="Kilometraje de Regreso", null=True)
    personal_a_cargo = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='salidas_a_cargo')
    descripcion = models.TextField(verbose_name="Reporte / Novedades", blank=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='salidas_creadas')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_hora_salida']

    def __str__(self):
        return f"{self.motivo} - {self.fecha_hora_salida.strftime('%d/%m/%Y %H:%M')}"

    @property
    def kilometros_recorridos(self):
        if self.kilometraje_regreso is not None and self.kilometraje_salida is not None:
            return self.kilometraje_regreso - self.kilometraje_salida
        return None

class SalidaTerrenoUnidad(models.Model):
    salida = models.ForeignKey(
        SalidaTerreno,
        on_delete=models.CASCADE,
        related_name='asistencias_unidades',
    )
    unidad = models.ForeignKey(
        'Vehiculo',
        on_delete=models.CASCADE,
        related_name='asistencias_salidas',
    )
    asistentes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='asistencias_salidas_terreno',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['salida', 'unidad'], name='unique_unidad_por_salida_terreno'),
        ]

    def __str__(self):
        return f"{self.unidad.nombre} - {self.salida.motivo}"

class Emergencia(models.Model):
    TIPO_EMERGENCIA_CHOICES = [
        ('10-0', '10-0 — Llamado estructural'),
        ('10-0-1', '10-0-1 — Incendio estructural'),
        ('10-0-2', '10-0-2 — Edificio de cuatro o más pisos'),
        ('10-0-3', '10-0-3 — Lugar público en horario de funcionamiento'),
        ('10-0-4', '10-0-4 — Incendio estructural industrial'),
        ('10-0-5', '10-0-5 — Incendio estructural Hazmat'),
        ('10-0-15', '10-0-15 — Incendio rural'),
        ('10-0-7', '10-0-7 — Inflamación de ducto'),
        ('10-1-1', '10-1-1 — Incendio vehicular menor'),
        ('10-1-2', '10-1-2 — Incendio de vehículo de carga'),
        ('10-1-3', '10-1-3 — Incendio de vehículo con pasajeros'),
        ('10-1-4', '10-1-4 — Incendio de maquinaria agrícola, pesada o forestal'),
        ('10-1-5', '10-1-5 — Incendio de aeronave'),
        ('10-1-6', '10-1-6 — Incendio en vehículo a gas'),
        ('10-1-7', '10-1-7 — Incendio en vehículo eléctrico'),
        ('10-2-1', '10-2-1 — Incendio de pastizal urbano'),
        ('10-2-2', '10-2-2 — Incendio de pastizal rural'),
        ('10-2-3', '10-2-3 — Incendio agrícola'),
        ('10-2-4', '10-2-4 — Incendio de microbasural'),
        ('10-2-6', '10-2-6 — Vertedero'),
        ('10-3', '10-3 — Rescate de persona'),
        ('10-4', '10-4 — Rescate vehicular'),
        ('10-4-1', '10-4-1 — Rescate vehicular de vehículo menor'),
        ('10-4-2', '10-4-2 — Rescate de vehículo de carga, maquinaria o transporte'),
        ('10-4-3', '10-4-3 — Rescate vehicular en desnivel, aguas o quebradas'),
        ('10-4-4', '10-4-4 — Rescate vehicular de vehículos de emergencia'),
        ('10-4-5', '10-4-5 — Rescate vehicular relacionado con Hazmat'),
        ('10-5-1', '10-5-1 — Derrame de hidrocarburos'),
        ('10-5-2', '10-5-2 — Incidente con materiales peligrosos'),
        ('10-5-3', '10-5-3 — Atentado con elementos químicos, biológicos o radiológicos'),
        ('10-6-1', '10-6-1 — Emanación de gas combustible'),
        ('10-6-2', '10-6-2 — Explosión de gas'),
        ('10-6-3', '10-6-3 — Explosión de gas con fuego'),
        ('10-6', '10-6 — Emanación de gas'),
        ('10-7', '10-7 — Riesgo eléctrico'),
        ('10-7-1', '10-7-1 — Eléctrico habitacional, comercial o industrial'),
        ('10-7-2', '10-7-2 — Eléctrico en cámara, transformador o subestación'),
        ('10-8', '10-8 — Llamado no clasificado'),
        ('10-8-8', '10-8-8 — Rastreo de persona'),
        ('10-8-10', '10-8-10 — Rastreo en aguas abiertas'),
        ('10-8-11', '10-8-11 — Recuperación de cadáver'),
        ('10-8-12', '10-8-12 — Instrucción, asesorías o capacitación'),
        ('10-8-13', '10-8-13 — Caída de árbol'),
        ('10-8-14', '10-8-14 — Voladuras de techo'),
        ('10-8-15', '10-8-15 — Inundación'),
        ('10-8-16', '10-8-16 — Rescate de animal'),
        ('10-8-18', '10-8-18 — Derrame'),
        ('10-9-1', '10-9-1 — Peritaje solicitado por el Ministerio Público'),
        ('10-9-2', '10-9-2 — Revisión de edificios'),
        ('10-9-3', '10-9-3 — Inspección de local comercial'),
        ('10-9-4', '10-9-4 — Inspección de industrias'),
        ('10-9-5', '10-9-5 — Inspección de grifo'),
        ('10-9-6', '10-9-6 — Simulacros o ejercicios a terceros'),
        ('10-9-7', '10-9-7 — Inspección'),
        ('10-9-19', '10-9-19 — Instrucción, asesorías o capacitación'),
        ('10-10-1', '10-10-1 — Rebrote estructural'),
        ('10-10-2', '10-10-2 — Rebrote forestal'),
        ('10-10', '10-10 — Rebrote de fuego'),
        ('10-11', '10-11 — Servicio o accidente aéreo'),
        ('10-12', '10-12 — Apoyo a otros Cuerpos'),
        ('10-13', '10-13 — Artefacto explosivo o acto terrorista'),
        ('10-14', '10-14 — Accidente de aviación'),
        ('9-3', '9-3 — Acuartelamiento general (histórico)'),
        ('9-4', '9-4 — Acuartelamiento preventivo (histórico)'),
        ('10-1', 'Código histórico 10-1 — Incendio forestal'),
        ('10-2', 'Código histórico 10-2 — Rescate vehicular'),
        ('otro', 'Otro — Tipo de emergencia especificado'),
        ('Otro', 'Otro'),
    ]
    ESTADO_CHOICES = [
        ('Activa', 'Activa'),
        ('Controlada', 'Controlada'),
        ('Finalizada', 'Finalizada'),
    ]

    tipo = models.CharField(max_length=50, choices=TIPO_EMERGENCIA_CHOICES, default='Otro')
    tipo_historico = models.CharField(max_length=200, blank=True, default='')
    direccion = models.CharField(max_length=255, null=True, blank=True)
    fecha_hora_alarma = models.DateTimeField(null=True, blank=True)
    descripcion = models.TextField(verbose_name="Detalles del Incidente", null=True, blank=True)
    unidades_despachadas = models.CharField(max_length=100, help_text="Ej: B-1, R-2, Z-3", null=True, blank=True)
    oficial_a_cargo = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='emergencias_a_cargo')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Activa')
    asistentes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='emergencias_asistidas', blank=True, verbose_name='Personal Asistente')
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='emergencias_creadas')
    creado_en = models.DateTimeField(auto_now_add=True)
    documento_adjunto = models.FileField(upload_to=SecureFilePath('emergencias_docs/'), null=True, blank=True, validators=[validar_extension_archivo])
    registro_completado = models.BooleanField(default=False, verbose_name="Registro Completado")

    class Meta:
        ordering = ['-fecha_hora_alarma']

    def get_tipo_display(self):
        return self.tipo_historico or dict(self.TIPO_EMERGENCIA_CHOICES).get(self.tipo, self.tipo)

    def save(self, *args, **kwargs):
        if self.pk and self.tipo_historico:
            anterior = type(self).objects.filter(pk=self.pk).values_list('tipo', flat=True).first()
            if anterior is not None and anterior != self.tipo:
                self.tipo_historico = ''
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.direccion}"

class EmergenciaUnidad(models.Model):
    emergencia = models.ForeignKey(
        Emergencia,
        on_delete=models.CASCADE,
        related_name='unidades_asistencia',
    )
    unidad = models.ForeignKey(
        'Vehiculo',
        on_delete=models.CASCADE,
        related_name='asistencias_emergencias',
    )
    asistentes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='asistencias_emergencias_unidad',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['emergencia', 'unidad'], name='unique_unidad_por_emergencia'),
        ]

    def __str__(self):
        return f"{self.unidad.nombre} - {self.emergencia.get_tipo_display()}"

class FacilitadorCapacitacion(models.Model):
    TIPO_CHOICES = [
        ('instructor', 'Instructor'),
        ('entidad_externa', 'Entidad externa'),
        ('sin_clasificar', 'Referencia histórica por clasificar'),
    ]

    nombre = models.CharField(max_length=150, unique=True)
    tipo = models.CharField(max_length=24, choices=TIPO_CHOICES, default='instructor')
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['tipo', 'nombre']
        verbose_name = 'Instructor o entidad externa'
        verbose_name_plural = 'Instructores y entidades externas'

    def __str__(self):
        return f'{self.nombre} — {self.get_tipo_display()}'


class Capacitacion(models.Model):
    CLAVES_CITACION_CURSO = [(f'10-{numero}', f'10-{numero}') for numero in range(20, 31)]
    MALLA_CHOICES = [
        ('Nivel postulante', 'Nivel postulante'),
        ('Nivel inicial', 'Nivel inicial'),
        ('Nivel operativo', 'Nivel operativo'),
        ('Nivel profesional', 'Nivel profesional'),
        ('Nivel especialidad', 'Nivel especialidad'),
        ('Cursos complementarios', 'Cursos complementarios'),
        ('Otros', 'Otros'),
    ]
    
    TIPO_ACTIVIDAD_CHOICES = [
        ('Curso', 'Curso'),
        ('Reunión', 'Reunión'),
        ('Ejercicio de compañía', 'Ejercicio de compañía'),
        ('Campaña económica', 'Campaña económica'),
        ('Charla', 'Charla'),
        ('Visita', 'Visita'),
        ('Otro', 'Otro'),
    ]

    nombre = models.CharField(max_length=200)
    clave_citacion_curso = models.CharField(
        max_length=5, choices=CLAVES_CITACION_CURSO, blank=True, default='',
        verbose_name='Citación o curso',
    )
    tipo_actividad = models.CharField(max_length=50, choices=TIPO_ACTIVIDAD_CHOICES, default='Curso', verbose_name='Tipo de Actividad')
    malla = models.CharField(max_length=50, choices=MALLA_CHOICES, default='Otros', verbose_name='Malla/Curso')
    curso_malla = models.ForeignKey(
        'CursoMalla', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='capacitaciones_registradas', verbose_name='Curso oficial de la Malla Curricular',
    )
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)
    lugar = models.CharField(max_length=255)
    instructor = models.CharField(max_length=150)
    facilitador = models.ForeignKey(
        FacilitadorCapacitacion, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='capacitaciones', verbose_name='Instructor o entidad externa',
    )
    cupos = models.PositiveIntegerField(null=True, blank=True, help_text="Dejar en blanco si no hay límite")
    asistentes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='capacitaciones_asistidas', blank=True)
    companias_invitadas = models.ManyToManyField(Compania, related_name='capacitaciones_invitadas', blank=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='capacitaciones_creadas')
    documento_adjunto = models.FileField(upload_to=SecureFilePath('reuniones/'), null=True, blank=True, validators=[validar_extension_archivo])
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

    def __str__(self):
        return self.nombre


class CursoMalla(models.Model):
    NIVELES = [
        ('Nivel postulante', 'Nivel postulante'),
        ('Nivel inicial', 'Nivel inicial'),
        ('Nivel operativo', 'Nivel operativo'),
        ('Nivel profesional', 'Nivel profesional'),
        ('Cursos complementarios', 'Cursos complementarios'),
    ]

    nombre = models.CharField(max_length=220, unique=True)
    nivel = models.CharField(max_length=40, choices=NIVELES)
    orden = models.PositiveSmallIntegerField(default=0)
    complementario = models.BooleanField(default=False)
    aula_virtual = models.BooleanField(default=False)
    usuarios = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='ramos_malla_curricular',
    )

    class Meta:
        ordering = ['nivel', 'orden', 'nombre']
        verbose_name = 'Ramo de la malla curricular'
        verbose_name_plural = 'Ramos de la malla curricular'

    def __str__(self):
        return self.nombre

class Notificacion(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notificaciones_recibidas')
    mensaje = models.CharField(max_length=255)
    leida = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.mensaje

class Mantenimiento(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('En Progreso', 'En Progreso'),
        ('Finalizado', 'Finalizado'),
    ]
    TIPO_CHOICES = [
        ('Preventivo', 'Preventivo'),
        ('Correctivo', 'Correctivo'),
    ]

    vehiculo = models.CharField(max_length=100, help_text="Ej: Hyundai - XYZ123")
    fecha = models.DateField()
    fecha_resolucion = models.DateField(null=True, blank=True, verbose_name="Fecha de Resolución")
    descripcion = models.TextField()
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='mantenimientos_responsable')
    compania_caja = models.ForeignKey(Compania, on_delete=models.SET_NULL, null=True, blank=True, related_name='mantenimientos_pagados', verbose_name="Caja de Compañía")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='Preventivo')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"Mantenimiento de {self.vehiculo} el {self.fecha}"

    def save(self, *args, **kwargs):
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.fecha_resolucion and self.fecha_resolucion <= today:
            self.estado = 'Finalizado'
        elif self.fecha and self.fecha <= today:
            self.estado = 'En Progreso'
        else:
            self.estado = 'Pendiente'
            
        super().save(*args, **kwargs)

class ArchivoMantenimiento(models.Model):
    mantenimiento = models.ForeignKey(Mantenimiento, related_name='archivos', on_delete=models.CASCADE)
    archivo = models.FileField(upload_to=SecureFilePath('mantenimientos_archivos/'), validators=[validar_extension_archivo])
    subido_en = models.DateTimeField(auto_now_add=True)

class Vehiculo(models.Model):
    ESTADO_CHOICES = [
        ('Disponible', 'Operativo'),
        ('En Servicio', 'En Servicio'),
        ('En Taller', 'En Taller'),
        ('Fuera de Servicio', 'Fuera de Servicio'),
    ]

    COMBUSTIBLE_CHOICES = [
        ('Diesel', 'Diésel'),
        ('Gasolina', 'Gasolina'),
        ('Otro', 'Otro'),
    ]
    BOMBA_UNIDAD_CHOICES = [
        ('LPM', 'L/min'),
        ('GPM', 'GPM'),
    ]

    nombre = models.CharField(max_length=80, verbose_name="Nombre / Código del Carro")
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE, related_name='vehiculos', verbose_name="Compañía")
    patente = models.CharField(max_length=15, verbose_name="Patente")
    responsable_documentacion = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehiculos_responsable_documentacion',
        verbose_name='Responsable de documentación',
    )
    descripcion = models.TextField(max_length=500, null=True, blank=True, verbose_name="Descripción")
    marca = models.CharField(max_length=80, default='', verbose_name="Marca")
    modelo = models.CharField(max_length=80, default='', verbose_name="Modelo")
    anio_fabricacion = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Año de fabricación")
    anio_puesta_servicio = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Año de puesta en servicio")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Disponible')

    # Datos técnicos y legales de la hoja de vida (se completan desde su ficha).
    combustible = models.CharField(max_length=20, choices=COMBUSTIBLE_CHOICES, blank=True, default='')
    capacidad_estanque_litros = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    capacidad_estanque_agua_litros = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    capacidad_bomba = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    capacidad_bomba_unidad = models.CharField(max_length=4, choices=BOMBA_UNIDAD_CHOICES, blank=True, default='')
    horometro = models.DecimalField(max_digits=10, decimal_places=1, null=True, blank=True)
    odometro_actual = models.PositiveIntegerField(null=True, blank=True, verbose_name='Odómetro actual (km)')
    revision_tecnica_vencimiento = models.DateField(null=True, blank=True)
    revision_tecnica_archivo = models.FileField(
        upload_to=SecureFilePath('vehiculos_documentacion/'),
        validators=[validar_documento_vehiculo],
        null=True,
        blank=True,
        verbose_name='Documento de revisión técnica',
    )
    permiso_circulacion_vencimiento = models.DateField(null=True, blank=True)
    permiso_circulacion_archivo = models.FileField(
        upload_to=SecureFilePath('vehiculos_documentacion/'),
        validators=[validar_documento_vehiculo],
        null=True,
        blank=True,
        verbose_name='Documento de permiso de circulación',
    )
    soap_vencimiento = models.DateField(null=True, blank=True)
    seguro_numero_poliza = models.CharField(max_length=100, blank=True, default='')
    seguro_vencimiento = models.DateField(null=True, blank=True)
    neumaticos_estado = models.CharField(max_length=160, blank=True, default='')
    neumaticos_ultimo_cambio = models.DateField(null=True, blank=True)
    bateria_fecha_instalacion = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} ({self.compania.nombre})"


class LicenciaMedica(models.Model):
    integrante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='licencias_medicas',
    )
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE, related_name='licencias_medicas')
    fecha_inicio = models.DateField(verbose_name='Fecha de inicio')
    fecha_termino = models.DateField(verbose_name='Fecha de término')
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='licencias_medicas_registradas',
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha_termino', 'integrante__apellido', 'integrante__nombre']
        verbose_name = 'Licencia médica'
        verbose_name_plural = 'Licencias médicas'

    def __str__(self):
        return f'{self.integrante.get_full_name()} · {self.fecha_inicio} a {self.fecha_termino}'


class RondaVehiculo(models.Model):
    TIPO_HALLAZGO_CHOICES = [
        ('Sin novedad', 'Sin novedad'),
        ('Falla', 'Falla'),
        ('Observación', 'Observación'),
        ('Otro', 'Otro'),
    ]

    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='rondas')
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rondas_vehiculos',
    )
    fecha = models.DateTimeField(auto_now_add=True)
    tipo_hallazgo = models.CharField(max_length=20, choices=TIPO_HALLAZGO_CHOICES, default='Sin novedad')
    detalle = models.TextField(verbose_name='Falla, observación o detalle')
    estado_operativo = models.CharField(max_length=20, choices=Vehiculo.ESTADO_CHOICES, blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Ronda de vehículo'
        verbose_name_plural = 'Rondas de vehículos'

    def __str__(self):
        return f"Ronda de {self.vehiculo.nombre} ({self.fecha:%d/%m/%Y})"


class RegistroOperativo(models.Model):
    TIPO_CHOICES = [
        ('emergencia', 'Emergencia'),
        ('emergencia_vehicular', 'Emergencia vehicular (10-4)'),
        ('servicio_especial', 'Servicio especial'),
        ('practica_maquinista', 'Práctica de aspirante a maquinista (6-18)'),
        ('rodaje', 'Rodaje'),
        ('se_dirige_6_13', 'Se dirige a (6-13)'),
        ('rodaje_6_13', 'Registro histórico: Se dirige a (6-13) — Rodaje'),
        ('combustible_6_14', 'Carga de combustible (6-14)'),
        ('ronda_maquinistas', 'Ronda de maquinistas'),
        ('llegada_cuartel', 'Voluntarios llegados al cuartel'),
    ]
    APOYO_CHOICES = [
        ('municipalidad', 'Municipalidad'),
        ('carabineros', 'Carabineros'),
        ('ambulancia', 'Ambulancia'),
        ('pdi', 'PDI'),
        ('conaf', 'CONAF'),
        ('cmpc', 'CMPC'),
        ('ruta_5_sur', 'Asistencia Ruta 5 Sur'),
        ('otro_cuerpo', 'Otro Cuerpo de Bomberos'),
        ('otros', 'Otros'),
    ]
    ESTACION_CHOICES = [
        ('copec', 'Copec'), ('shell', 'Shell'), ('aramco', 'Aramco'), ('otra', 'Otra'),
    ]
    COMBUSTIBLE_CHOICES = [
        ('diesel', 'Diésel'), ('bencina_93', 'Bencina 93'),
        ('bencina_95', 'Bencina 95'), ('bencina_97', 'Bencina 97'), ('otro', 'Otro'),
    ]

    tipo = models.CharField(max_length=32, choices=TIPO_CHOICES)
    codigo = models.CharField(max_length=80, blank=True, default='')
    fecha_inicio = models.DateField()
    fecha_termino = models.DateField(null=True, blank=True)
    hora_despacho = models.TimeField(null=True, blank=True)
    hora_llegada = models.TimeField(null=True, blank=True)
    kilometraje_despacho = models.PositiveIntegerField(null=True, blank=True)
    kilometraje_llegada = models.PositiveIntegerField(null=True, blank=True)
    direccion = models.CharField(max_length=255, blank=True, default='')
    estacion_servicio = models.CharField(max_length=30, choices=ESTACION_CHOICES, blank=True, default='')
    estacion_detalle = models.CharField(max_length=180, blank=True, default='')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, null=True, blank=True, related_name='registros_operativos')
    maquinista = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='registros_operativos_conduccion')
    obac = models.CharField(max_length=160, blank=True, default='')
    obac_voluntario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='registros_operativos_obac',
    )
    instituciones_apoyo = models.JSONField(default=list, blank=True)
    apoyo_otro_cuerpo = models.CharField(max_length=160, blank=True, default='')
    apoyo_otros = models.CharField(max_length=255, blank=True, default='')
    informe = models.TextField(blank=True, default='')
    novedades_unidad = models.TextField(blank=True, default='')
    lesionados_externos = models.TextField(blank=True, default='')
    involucrados = models.JSONField(default=list, blank=True)
    autorizaciones = models.JSONField(default=list, blank=True)
    autorizado_por = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name='registros_operativos_autorizados',
    )
    aspirante_nombre = models.CharField(max_length=160, blank=True, default='')
    aspirante_clave = models.CharField(max_length=40, blank=True, default='')
    aspirante_voluntario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='registros_operativos_como_aspirante',
    )
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='practicas_maquinista_instructor')
    combustible_tipo = models.CharField(max_length=20, choices=COMBUSTIBLE_CHOICES, blank=True, default='')
    monto_combustible = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    checklist = models.JSONField(default=list, blank=True)
    emergencia = models.ForeignKey('Emergencia', on_delete=models.SET_NULL, null=True, blank=True, related_name='registros_operativos')
    salida_terreno = models.ForeignKey('SalidaTerreno', on_delete=models.SET_NULL, null=True, blank=True, related_name='registros_operativos')
    movimiento_caja = models.OneToOneField('CajaChica', on_delete=models.SET_NULL, null=True, blank=True, related_name='registro_operativo')
    asistentes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='asistencias_registros_operativos')
    unidades = models.ManyToManyField(
        'Vehiculo', through='RegistroOperativoUnidad', blank=True,
        related_name='registros_operativos_asignados',
    )
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='registros_operativos_creados')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_inicio', '-creado_en']
        verbose_name = 'Registro operativo'
        verbose_name_plural = 'Registros operativos'

    @property
    def kilometros_recorridos(self):
        if self.kilometraje_despacho is not None and self.kilometraje_llegada is not None:
            return self.kilometraje_llegada - self.kilometraje_despacho
        return None

    @property
    def horas_practica(self):
        if self.hora_despacho and self.hora_llegada:
            inicio = self.hora_despacho.hour * 60 + self.hora_despacho.minute
            termino = self.hora_llegada.hour * 60 + self.hora_llegada.minute
            if termino < inicio:
                termino += 24 * 60
            return (termino - inicio) / 60
        return None

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.fecha_inicio:%d/%m/%Y}'


class RegistroOperativoUnidad(models.Model):
    registro = models.ForeignKey(RegistroOperativo, on_delete=models.CASCADE, related_name='unidades_asignadas')
    unidad = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='detalles_registros_operativos')
    asistentes = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='asistencias_por_unidad_operativa')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['registro', 'unidad'], name='unique_unidad_por_registro_operativo'),
        ]
        ordering = ['unidad__nombre']

    def __str__(self):
        return f'{self.unidad.nombre} — {self.registro}'

class Inventario(models.Model):
    ESTADO_CHOICES = [
        ('Bueno', 'Bueno'),
        ('Regular', 'Regular'),
        ('Malo', 'Malo'),
        ('En Reparación', 'En Reparación'),
        ('De Baja', 'De Baja'),
    ]

    ITEM_CHOICES = [
        ('Casco de bombero', 'Casco de bombero (F1, F2, etc.)'),
        ('Equipo de respiración autónoma (ERA)', 'Equipo de respiración autónoma (ERA)'),
        ('Traje estructural', 'Traje estructural (chaquetón y pantalón)'),
        ('Botas estructurales', 'Botas estructurales'),
        ('Guantes de bombero', 'Guantes de bombero'),
        ('Monja / capucha ignífuga', 'Monja / capucha ignífuga'),
        ('Linterna para casco', 'Linterna para casco'),
        ('Hacha de bombero', 'Hacha de bombero'),
        ('Herramienta Halligan', 'Herramienta Halligan'),
        ('Manguera de 1.5 pulgadas', 'Manguera de 1.5"'),
        ('Manguera de 2.5 pulgadas', 'Manguera de 2.5"'),
        ('Pitón / Lanza de agua', 'Pitón / Lanza de agua'),
        ('Escala de extensión', 'Escala de extensión'),
        ('Cámara térmica', 'Cámara térmica'),
        ('Detector de gases', 'Detector de gases'),
        ('Otro', 'Otro (especificar en descripción)'),
    ]

    ITEM_CHOICES_DICT = dict(ITEM_CHOICES)

    nombre = models.CharField(max_length=200)
    compania = models.ForeignKey(Compania, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventario')
    ubicacion = models.CharField(max_length=150, help_text="Ej: Bodega 1, Carro B-2")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Bueno')
    fecha_adquisicion = models.DateField(null=True, blank=True)
    asignado_a = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventario_asignado')
    asignado_a_vehiculo = models.ForeignKey(Vehiculo, on_delete=models.SET_NULL, null=True, blank=True, related_name='inventario_asignado', verbose_name="Asignado a Carro")
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    agregado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='inventario_agregado')
    agregado_en = models.DateTimeField(auto_now_add=True)
    valor = models.IntegerField(null=True, blank=True, verbose_name="Valor ($)", help_text="Valor estimado o de compra")

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        if self.asignado_a:
            asignacion = f"Asignado a: {self.asignado_a.get_full_name()}"
        elif self.asignado_a_vehiculo:
            asignacion = f"Asignado a Carro: {self.asignado_a_vehiculo.nombre}"
        else:
            asignacion = "Sin asignar / Bodega"
        return f"{self.get_nombre_display()} - {asignacion}"

    @staticmethod
    def get_nombre_completo(nombre_clave):
        return Inventario.ITEM_CHOICES_DICT.get(nombre_clave, nombre_clave)
        
    def get_nombre_display(self):
        return Inventario.ITEM_CHOICES_DICT.get(self.nombre, self.nombre)

    def save(self, *args, **kwargs):
        # Guardamos primero para asegurarnos de que el objeto tiene un 'pk' (ID)
        # si es una nueva instancia.
        super().save(*args, **kwargs)

        qr_updated = False
        # Generar QR solo si hay un usuario o carro asignado
        if self.asignado_a or self.asignado_a_vehiculo:
            # Usamos un formato simple y robusto: solo el ID del ítem.
            qr_content = str(self.id)
            qr_img = qrcode.make(qr_content)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            file_name = f'item_{self.id}.png'
            self.qr_code.save(file_name, File(buffer), save=False)
            qr_updated = True
        
        # Si se desasigna de ambos, limpiar el QR
        elif not self.asignado_a and not self.asignado_a_vehiculo and self.qr_code:
            self.qr_code.delete(save=False)
            qr_updated = True

        if qr_updated:
            # Guardamos los cambios del QR en una sola llamada para evitar bucles
            super().save(update_fields=['qr_code'])


class DevolucionInventario(models.Model):
    item = models.ForeignKey(Inventario, on_delete=models.SET_NULL, null=True, blank=True, related_name='devoluciones')
    compania = models.ForeignKey(Compania, on_delete=models.SET_NULL, null=True, blank=True, related_name='devoluciones_inventario')
    compania_nombre = models.CharField(max_length=80, blank=True)
    nombre_item = models.CharField(max_length=200)
    entregado_a = models.CharField(max_length=160, blank=True)
    ubicacion_anterior = models.CharField(max_length=150, blank=True)
    ubicacion_retorno = models.CharField(max_length=150)
    estado_retorno = models.CharField(max_length=20, choices=Inventario.ESTADO_CHOICES)
    observaciones = models.TextField(blank=True)
    acta = models.FileField(
        upload_to=SecureFilePath('devoluciones/actas/'),
        validators=[validar_extension_archivo],
        blank=True,
    )
    realizado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='devoluciones_inventario_registradas')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']
        verbose_name = 'Devolución de inventario'
        verbose_name_plural = 'Devoluciones de inventario'

    def __str__(self):
        return f'Devolución de {self.nombre_item} ({self.creado_en:%d/%m/%Y})'


class DevolucionInventarioFoto(models.Model):
    devolucion = models.ForeignKey(DevolucionInventario, on_delete=models.CASCADE, related_name='fotos')
    archivo = models.ImageField(
        upload_to=SecureFilePath('devoluciones/fotos/'),
        validators=[validar_extension_imagen],
    )

    def __str__(self):
        return f'Fotografía de {self.devolucion.nombre_item}'

class CajaChica(models.Model):
    TIPO_MOVIMIENTO_CHOICES = [
        ('Ingreso', 'Ingreso'),
        ('Egreso', 'Egreso'),
    ]
    TIPO_CUENTA_CHOICES = [
        ('caja_propia', 'Caja propia'),
        ('cuenta_bancaria', 'Cuenta bancaria'),
    ]

    fecha = models.DateTimeField(default=timezone.now)
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO_CHOICES)
    tipo_cuenta = models.CharField(
        max_length=20,
        choices=TIPO_CUENTA_CHOICES,
        blank=True,
        default='',
        verbose_name='Tipo de cuenta',
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.CharField(max_length=255)
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE, null=True, blank=True, related_name='movimientos_caja')
    documento_adjunto = models.FileField(upload_to=SecureFilePath('caja_chica/'), null=True, blank=True, validators=[validar_extension_archivo])

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Movimiento de Caja Chica"
        verbose_name_plural = "Movimientos de Caja Chica"


class CuotaVoluntario(models.Model):
    voluntario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cuotas_voluntario',
    )
    compania = models.ForeignKey(
        Compania,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cuotas_voluntarios',
    )
    anio = models.PositiveSmallIntegerField()
    mes = models.PositiveSmallIntegerField()
    movimiento = models.OneToOneField(
        CajaChica,
        on_delete=models.CASCADE,
        related_name='cuota_voluntario',
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['voluntario__nombre', 'voluntario__apellido', 'mes']
        constraints = [
            models.UniqueConstraint(
                fields=['voluntario', 'anio', 'mes'],
                name='unique_cuota_voluntario_mes',
            ),
            models.CheckConstraint(
                condition=models.Q(mes__gte=1, mes__lte=12),
                name='cuota_voluntario_mes_1_12',
            ),
        ]

class Aviso(models.Model):
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='avisos_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha_creacion']

class AvisoDestinatario(models.Model):
    aviso = models.ForeignKey(Aviso, on_delete=models.CASCADE, related_name='destinatarios')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='avisos_asignados')
    leido = models.BooleanField(default=False)
    fecha_lectura = models.DateTimeField(null=True, blank=True)


class ReporteError(models.Model):
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_CORREGIDO = 'corregido'
    ESTADO_CHOICES = [
        (ESTADO_PENDIENTE, 'En espera'),
        (ESTADO_CORREGIDO, 'Corregido'),
    ]

    nombre = models.CharField(max_length=120, verbose_name='Nombre del error')
    descripcion = models.TextField(max_length=5000, verbose_name='Descripción del error')
    reportante_nombre = models.CharField(max_length=200, verbose_name='Nombre del reportante')
    reportante_compania = models.CharField(max_length=80, blank=True, default='', verbose_name='Compañía del reportante')
    reportante_rol = models.CharField(max_length=80, blank=True, default='', verbose_name='Rol del reportante')
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reportes_errores_creados',
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default=ESTADO_PENDIENTE, db_index=True)
    corregido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reportes_errores_corregidos',
    )
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'Reporte de error'
        verbose_name_plural = 'Reportes de errores'

    def __str__(self):
        return f'{self.nombre} ({self.get_estado_display()})'


class GuiaChatbot(models.Model):
    MODULO_CHOICES = [
        ('dashboard', 'Inicio'),
        ('inventario', 'Inventario'),
        ('emergencias', 'Emergencias'),
        ('salidas', 'Salidas a terreno'),
        ('caja', 'Caja'),
        ('documentos', 'Documentos'),
        ('capacitaciones', 'Cursos y capacitaciones'),
        ('malla', 'Malla curricular'),
        ('mantenimiento', 'Mantenimiento'),
        ('proyectos', 'Proyectos'),
        ('resumen', 'Resumen General'),
        ('inspectores', 'Inspectores'),
        ('qr', 'Escanear QR'),
        ('administracion', 'Administración'),
    ]

    titulo = models.CharField(max_length=160)
    palabras_clave = models.TextField(
        help_text='Separa las palabras o frases con coma o una línea nueva.'
    )
    pasos = models.TextField(help_text='Instrucciones breves, una por línea.')
    modulo = models.CharField(max_length=24, choices=MODULO_CHOICES, default='dashboard')
    prioridad = models.PositiveSmallIntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['-prioridad', 'titulo']
        verbose_name = 'Guía del chatbot'
        verbose_name_plural = 'Guías del chatbot'

    def __str__(self):
        return self.titulo


class ComandoChatbot(models.Model):
    HANDLER_CHOICES = [
        ('inventario_resumen', 'Resumen de inventario'),
        ('emergencias_activas', 'Emergencias activas'),
        ('caja_saldo', 'Saldo de caja'),
    ]

    MODULO_CHOICES = [
        ('inventario', 'Inventario'),
        ('emergencias', 'Emergencias'),
        ('caja', 'Caja'),
    ]

    nombre = models.CharField(max_length=120, unique=True)
    palabras_clave = models.TextField(
        help_text='Separa las palabras o frases con coma o una línea nueva.'
    )
    handler = models.CharField(max_length=40, choices=HANDLER_CHOICES)
    modulo_requerido = models.CharField(max_length=24, choices=MODULO_CHOICES)
    prioridad = models.PositiveSmallIntegerField(default=0)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['-prioridad', 'nombre']
        verbose_name = 'Comando de consulta del chatbot'
        verbose_name_plural = 'Comandos de consulta del chatbot'

    def __str__(self):
        return self.nombre

class PasswordResetCode(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=6)
    creado_en = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)
    intentos = models.PositiveIntegerField(default=0)

    def is_valid(self):
        from django.utils import timezone
        import datetime
        now = timezone.now()
        creado_en_aware = self.creado_en
        if timezone.is_naive(self.creado_en):
            creado_en_aware = timezone.make_aware(self.creado_en, timezone.get_current_timezone())
        return not self.usado and self.intentos < 5 and (now - creado_en_aware) < datetime.timedelta(minutes=15)


class RegistroPendiente(models.Model):
    email = models.EmailField(max_length=80, unique=True)
    nombre = models.CharField(max_length=80)
    apellido = models.CharField(max_length=80)
    rut = models.CharField(max_length=15)
    clave_radial = models.CharField(max_length=20, null=True, blank=True)
    compania = models.ForeignKey(Compania, on_delete=models.SET_NULL, null=True, blank=True)
    foto_perfil = models.ImageField(
        upload_to=SecureFilePath('registros_pendientes/'),
        null=True,
        blank=True,
        validators=[validar_extension_imagen],
    )
    password = models.CharField(max_length=128)
    codigo = models.CharField(max_length=6)
    creado_en = models.DateTimeField(default=timezone.now)
    intentos = models.PositiveIntegerField(default=0)

    def is_valid(self):
        return self.intentos <= 5 and (timezone.now() - self.creado_en) < datetime.timedelta(minutes=15)

    def __str__(self):
        return f"Registro pendiente para {self.email}"
