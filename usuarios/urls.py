from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    # Página raíz (redirige al login) y página de inicio
    path('', lambda request: redirect('login'), name='index'),
    path('inicio/', lambda request: redirect('dashboard'), name='inicio'),  

    # Página de registro
    path('registro_view/', views.registro_view, name='registro'), 

    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/summary/', views.dashboard_summary_view, name='dashboard_summary'),

    # Reportes
    path('reporte/anual/', views.generar_reporte_anual_pdf, name='generar_reporte_anual'),
    path('reporte/anual/excel/', views.generar_reporte_anual_excel, name='generar_reporte_anual_excel'),
    
    # Proyectos
    path('proyectos/', views.proyectos_view, name='proyectos'),
    path('proyectos/<int:proyecto_id>/edit/', views.proyecto_edit_view, name='proyecto_edit'),
    path('proyectos/<int:proyecto_id>/delete/', views.proyecto_delete_view, name='proyecto_delete'),

    # Documentos
    path('documentos/', views.documentos_view, name='documentos'),
    path('documentos/<int:doc_id>/delete/', views.documento_delete_view, name='documento_delete'),

    # Inventario
    path('inventario/', views.inventario_view, name='inventario'),
    path('inventario/<int:item_id>/edit/', views.inventario_edit_view, name='inventario_edit'),
    path('inventario/<int:item_id>/delete/', views.inventario_delete_view, name='inventario_delete'),
    path('inventario/assign/', views.inventario_assign_view, name='inventario_assign'),
    path('inventario/group/edit/', views.inventario_group_edit_view, name='inventario_group_edit'),
    path('inventario/group/delete/', views.inventario_group_delete_view, name='inventario_group_delete'),
    path('inventario/<int:item_id>/unassign/', views.inventario_unassign_view, name='inventario_unassign'),
    path('scan/', views.scan_qr_page_view, name='scan_qr_page'),
    path('inventario/qr-lookup/', views.inventario_qr_lookup_view, name='inventario_qr_lookup'),

    # Salidas a terreno
    path('salidas/', views.salidas_terreno_view, name='salidas_terreno'),
    path('salidas/<int:salida_id>/edit/', views.salida_terreno_edit_view, name='salida_terreno_edit'),
    path('salidas/<int:salida_id>/delete/', views.salida_terreno_delete_view, name='salida_terreno_delete'),

    # Emergencias
    path('emergencias/', views.emergencias_view, name='emergencias'),
    path('emergencias/<int:emergencia_id>/edit/', views.emergencia_edit_view, name='emergencia_edit'),
    path('emergencias/<int:emergencia_id>/delete/', views.emergencia_delete_view, name='emergencia_delete'),

    # Capacitaciones
    path('capacitaciones/', views.capacitaciones_view, name='capacitaciones'),
    path('capacitaciones/<int:capacitacion_id>/edit/', views.capacitacion_edit_view, name='capacitacion_edit'),
    path('capacitaciones/<int:capacitacion_id>/delete/', views.capacitacion_delete_view, name='capacitacion_delete'),

    # Mantenimiento
    path('mantenimiento/', views.mantenimiento_view, name='mantenimiento'),
    path('mantenimiento/<int:mantenimiento_id>/edit/', views.mantenimiento_edit_view, name='mantenimiento_edit'),
    path('mantenimiento/<int:mantenimiento_id>/delete/', views.mantenimiento_delete_view, name='mantenimiento_delete'),

    # Caja chica
    path('caja-chica/', views.caja_chica_view, name='caja_chica'),
    path('caja-chica/<int:movimiento_id>/edit/', views.caja_chica_edit_view, name='caja_chica_edit'),
    path('caja-chica/<int:movimiento_id>/delete/', views.caja_chica_delete_view, name='caja_chica_delete'),

    # Administración
    path('administracion/', views.administracion_view, name='administracion'),
    path('administracion/user/create/', views.user_create_view, name='user_create'),
    path('administracion/user/<int:user_id>/edit/', views.user_edit_view, name='user_edit'),
    path('administracion/user/<int:user_id>/approve/', views.user_approve_view, name='user_approve'),
    path('administracion/user/<int:user_id>/delete/', views.user_delete_view, name='user_delete'),

    # Administración - Roles
    path('administracion/rol/create/', views.rol_create_view, name='rol_create'),
    path('administracion/rol/<int:rol_id>/edit/', views.rol_edit_view, name='rol_edit'),
    path('administracion/rol/<int:rol_id>/delete/', views.rol_delete_view, name='rol_delete'),

    # Administración - Compañías
    path('administracion/compania/create/', views.compania_create_view, name='compania_create'),
    path('administracion/compania/<int:compania_id>/edit/', views.compania_edit_view, name='compania_edit'),
    path('administracion/compania/<int:compania_id>/delete/', views.compania_delete_view, name='compania_delete'),

    # Perfil de usuario
    path('perfil/', views.perfil_view, name='perfil'),
    
    # Notificaciones
    path('api/notificaciones/', views.api_notificaciones, name='api_notificaciones'),
    path('notificaciones/leer/<int:notif_id>/', views.marcar_notificacion_leida, name='marcar_notificacion_leida'),

    # Avisos 
    path('aviso/create/', views.aviso_create_view, name='aviso_create'),
    path('avisos/<int:destinatario_id>/leer/', views.aviso_leer_view, name='aviso_leer'),

]
