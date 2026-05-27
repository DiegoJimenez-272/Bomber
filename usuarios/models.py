from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
import qrcode
from io import BytesIO
from django.core.files import File
from django.db.models.signals import post_save
from django.dispatch import receiver

class Rol(models.Model):
    nombre = models.CharField(max_length=80)
    descripcion = models.TextField(max_length=1200)
    
    # --- Permisos de Acceso a Módulos ---
    ver_resumen_general = models.BooleanField(default=False, verbose_name="Resumen General")
    ver_documentacion = models.BooleanField(default=False, verbose_name="Documentación")
    ver_escanear_qr = models.BooleanField(default=False, verbose_name="Escanear QR")
    ver_inventario = models.BooleanField(default=False, verbose_name="Inventario")
    ver_salidas_terreno = models.BooleanField(default=False, verbose_name="Salidas a terreno")
    ver_emergencias = models.BooleanField(default=False, verbose_name="Emergencias")
    ver_capacitaciones = models.BooleanField(default=False, verbose_name="Cursos")
    ver_mantenimientos = models.BooleanField(default=False, verbose_name="Mantenimientos")
    ver_proyectos = models.BooleanField(default=False, verbose_name="Proyectos")
    ver_caja_chica = models.BooleanField(default=False, verbose_name="Caja Chica")
    ver_avisos = models.BooleanField(default=False, verbose_name="Avisos")

    # --- Permisos de Edición / Creación / Eliminación ---
    editar_documentacion = models.BooleanField(default=False, verbose_name="Editar Documentación")
    editar_inventario = models.BooleanField(default=False, verbose_name="Editar Inventario")
    editar_salidas_terreno = models.BooleanField(default=False, verbose_name="Editar Salidas a terreno")
    editar_emergencias = models.BooleanField(default=False, verbose_name="Editar Emergencias")
    editar_capacitaciones = models.BooleanField(default=False, verbose_name="Editar Cursos")
    editar_mantenimientos = models.BooleanField(default=False, verbose_name="Editar Mantenimientos")
    editar_proyectos = models.BooleanField(default=False, verbose_name="Editar Proyectos")
    editar_caja_chica = models.BooleanField(default=False, verbose_name="Editar Caja Chica")
    editar_avisos = models.BooleanField(default=False, verbose_name="Editar Avisos")

    def __str__(self):
        return self.nombre

class Compania(models.Model):
    nombre = models.CharField(max_length=80)
    ubicacion = models.CharField(max_length=80)
    logo = models.ImageField(upload_to='logos_companias/', null=True, blank=True, verbose_name='Logo de la Compañía')
    
    def __str__(self):
        return self.nombre 

class UsuarioManager(BaseUserManager):
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
    rut = models.CharField(max_length=12, unique=True, null=True, blank=True, verbose_name='RUT')
    clave_radial = models.CharField(max_length=20, null=True, blank=True, verbose_name='Clave Radial')
    rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True)
    compania = models.ForeignKey(Compania, on_delete=models.SET_NULL, null=True, blank=True)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', null=True, blank=True, verbose_name='Foto de Perfil')
    
    # Campos requeridos para AbstractBaseUser
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido', 'rut']
    
    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.email})"
    
    def get_full_name(self):
        return f"{self.nombre} {self.apellido}"
    
    def get_short_name(self):
        return self.nombre

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
    archivo = models.FileField(upload_to='proyectos_archivos/')
    subido_en = models.DateTimeField(auto_now_add=True)

class Documento(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to='documentos/')
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE, null=True, blank=True, related_name='documentos')
    subido_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    subido_en = models.DateTimeField(auto_now_add=True)

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
    kilometraje_salida = models.PositiveIntegerField(verbose_name="Kilometraje de Salida", default=0)
    kilometraje_regreso = models.PositiveIntegerField(verbose_name="Kilometraje de Regreso", null=True, blank=True)
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

class Emergencia(models.Model):
    TIPO_EMERGENCIA_CHOICES = [
        ('10-0-1', 'Llamado Estructural'),
        ('10-0-2', 'Llamado a Vehículo'),
        ('10-1', 'Incendio Forestal'),
        ('10-2', 'Rescate Vehicular'),
        ('10-3', 'Rescate de Personas'),
        ('10-4', 'Materiales Peligrosos'),
        ('Otro', 'Otro'),
    ]
    ESTADO_CHOICES = [
        ('Activa', 'Activa'),
        ('Controlada', 'Controlada'),
        ('Finalizada', 'Finalizada'),
    ]

    tipo = models.CharField(max_length=50, choices=TIPO_EMERGENCIA_CHOICES, default='Otro')
    direccion = models.CharField(max_length=255)
    fecha_hora_alarma = models.DateTimeField()
    descripcion = models.TextField(verbose_name="Detalles del Incidente")
    unidades_despachadas = models.CharField(max_length=100, help_text="Ej: B-1, R-2, Z-3")
    oficial_a_cargo = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='emergencias_a_cargo')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Activa')
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='emergencias_creadas')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_hora_alarma']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.direccion}"

class Capacitacion(models.Model):
    MALLA_CHOICES = [
        ('Nivel postulante', 'Nivel postulante'),
        ('Nivel inicial', 'Nivel inicial'),
        ('Nivel operativo', 'Nivel operativo'),
        ('Nivel profesional', 'Nivel profesional'),
        ('Nivel especialidad', 'Nivel especialidad'),
        ('Otros', 'Otros'),
    ]

    nombre = models.CharField(max_length=200)
    malla = models.CharField(max_length=50, choices=MALLA_CHOICES, default='Otros', verbose_name='Malla/Curso')
    descripcion = models.TextField()
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)
    lugar = models.CharField(max_length=255)
    instructor = models.CharField(max_length=150)
    cupos = models.PositiveIntegerField(null=True, blank=True, help_text="Dejar en blanco si no hay límite")
    asistentes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='capacitaciones_asistidas', blank=True)
    companias_invitadas = models.ManyToManyField(Compania, related_name='capacitaciones_invitadas', blank=True)
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='capacitaciones_creadas')
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = "Curso"
        verbose_name_plural = "Cursos"

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
    archivo = models.FileField(upload_to='mantenimientos_archivos/')
    subido_en = models.DateTimeField(auto_now_add=True)

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
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)
    agregado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='inventario_agregado')
    agregado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f"{self.get_nombre_display()} - Asignado a: {self.asignado_a.get_full_name() if self.asignado_a else 'Sin asignar'}"

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
        # Generar QR solo si hay un usuario asignado
        if self.asignado_a:
            # Usamos un formato simple y robusto: solo el ID del ítem.
            qr_content = str(self.id)
            qr_img = qrcode.make(qr_content)
            buffer = BytesIO()
            qr_img.save(buffer, format='PNG')
            file_name = f'item_{self.id}.png'
            self.qr_code.save(file_name, File(buffer), save=False)
            qr_updated = True
        
        # Si se desasigna el usuario, limpiar el QR
        elif not self.asignado_a and self.qr_code:
            self.qr_code.delete(save=False)
            qr_updated = True

        if qr_updated:
            # Guardamos los cambios del QR en una sola llamada para evitar bucles
            super().save(update_fields=['qr_code'])

class CajaChica(models.Model):
    TIPO_MOVIMIENTO_CHOICES = [
        ('Ingreso', 'Ingreso'),
        ('Egreso', 'Egreso'),
    ]

    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=10, choices=TIPO_MOVIMIENTO_CHOICES)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.CharField(max_length=255)
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    compania = models.ForeignKey(Compania, on_delete=models.CASCADE, null=True, blank=True, related_name='movimientos_caja')
    documento_adjunto = models.FileField(upload_to='caja_chica/', null=True, blank=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = "Movimiento de Caja Chica"
        verbose_name_plural = "Movimientos de Caja Chica"

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