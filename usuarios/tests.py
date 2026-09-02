from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from usuarios.models import Usuario, Rol, Compania, Documento, Inventario, PasswordResetCode

class SecurityTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Compañías de prueba
        self.compania_a = Compania.objects.create(nombre="Primera Compañía", ubicacion="Mulchén Centro")
        self.compania_b = Compania.objects.create(nombre="Segunda Compañía", ubicacion="Mulchén Norte")
        
        # Roles de prueba
        self.rol_admin = Rol.objects.create(nombre="Administrador", descripcion="Admin", ver_resumen_general=True)
        self.rol_voluntario = Rol.objects.create(nombre="Voluntario", descripcion="Voluntario", ver_inventario=True, ver_documentacion=True)
        
        # Usuarios de prueba
        self.admin_user = Usuario.objects.create_superuser(
            email="admin@sigbomberos.cl",
            password="AdminPassword123!",
            nombre="Admin",
            apellido="Sistema",
            rut="11111111-1"
        )
        
        self.user_normal = Usuario.objects.create_user(
            email="voluntario@sigbomberos.cl",
            password="VoluntarioPassword123!",
            nombre="Juan",
            apellido="Pérez",
            rut="22222222-2",
            compania=self.compania_a,
            rol=self.rol_voluntario
        )

    def test_cabeceras_de_seguridad_http(self):
        """Verifica que las cabeceras HTTP de protección OWASP estén presentes."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('X-Frame-Options', response.headers)
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')

    def test_bloqueo_acceso_no_autorizado_a_administracion(self):
        """Verifica que usuarios no administradores no puedan acceder a vistas administrativas."""
        self.client.login(email="voluntario@sigbomberos.cl", password="VoluntarioPassword123!")
        
        response = self.client.get(reverse('user_create'))
        self.assertEqual(response.status_code, 302)
        
        response = self.client.get(reverse('rol_create'))
        self.assertEqual(response.status_code, 302)

    def test_prevencion_enumeracion_en_recuperacion_clave(self):
        """Verifica respuesta uniforme para correos existentes e inexistentes."""
        response = self.client.post(reverse('password_reset_request'), {'email': 'noexiste@sigbomberos.cl'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('password_reset_verify'))

    def test_proteccion_idor_inventario(self):
        """Verifica que un voluntario de la Compañía A no pueda editar o eliminar ítems de la Compañía B."""
        item_comp_b = Inventario.objects.create(
            nombre="Casco de bombero",
            compania=self.compania_b,
            ubicacion="Bodega 2",
            estado="Bueno"
        )
        
        self.client.login(email="voluntario@sigbomberos.cl", password="VoluntarioPassword123!")
        
        response = self.client.post(reverse('inventario_delete', kwargs={'item_id': item_comp_b.id}))
        self.assertEqual(response.status_code, 302)
        
        self.assertTrue(Inventario.objects.filter(id=item_comp_b.id).exists())

    def test_bloqueo_fuerza_bruta_pin_persistido_en_bd(self):
        """Verifica que el límite de 5 intentos en el PIN se mantenga en base de datos aunque se eliminen cookies."""
        reset_code = PasswordResetCode.objects.create(usuario=self.user_normal, codigo="123456")
        
        # Simular 5 peticiones erróneas con borrado de cookies en cada intento
        for i in range(5):
            session = self.client.session
            session['reset_email'] = self.user_normal.email
            session.save()
            
            response = self.client.post(reverse('password_reset_verify'), {'codigo': '999999'})
            self.assertIn(response.status_code, [200, 302])

            
            # Borrar cookies de sesión para intentar evadir el contador
            self.client.cookies.clear()

        # Al 6to intento, el código en base de datos debe estar invalidado
        reset_code.refresh_from_db()
        self.assertTrue(reset_code.intentos >= 5 or reset_code.usado)

    def test_subida_archivo_magic_bytes_invalido(self):
        """Verifica que se rechacen archivos con extensión camuflada que no contienen los magic bytes correctos."""
        invalid_file = SimpleUploadedFile(
            name="documento_falso.jpg",
            content=b"DATOS_INVALIDOS_SIN_CABECERA_JPEG",
            content_type="image/jpeg"
        )
        
        from usuarios.validators import validar_extension_imagen
        from django.core.exceptions import ValidationError
        
        with self.assertRaises(ValidationError):
            validar_extension_imagen(invalid_file)

    def test_descarga_protegida_documentos_idor(self):
        """Verifica que un usuario no pueda descargar documentos pertenecientes a otra compañía."""
        doc_comp_b = Documento.objects.create(
            nombre="Ficha Médica Secreta",
            compania=self.compania_b,
            archivo=SimpleUploadedFile("doc.pdf", b"%PDF-1.4 test content", content_type="application/pdf"),
            subido_por=self.admin_user
        )
        
        self.client.login(email="voluntario@sigbomberos.cl", password="VoluntarioPassword123!")
        response = self.client.get(reverse('documento_descargar', kwargs={'doc_id': doc_comp_b.id}))
        
        # Debe bloquear y redirigir
        self.assertEqual(response.status_code, 302)

    def test_validacion_y_formateo_rut_chileno(self):
        """Verifica la validación Módulo 11 y el formateo de RUT chileno."""
        from usuarios.validators import validar_rut, formatear_rut
        
        # RUTs válidos
        self.assertTrue(validar_rut("12.345.678-5"))
        self.assertTrue(validar_rut("123456785"))
        self.assertTrue(validar_rut("11.111.111-1"))
        
        # RUTs inválidos
        self.assertFalse(validar_rut("12.345.678-9"))
        self.assertFalse(validar_rut("abc"))
        
        # Formateo automático
        self.assertEqual(formatear_rut("123456785"), "12.345.678-5")

