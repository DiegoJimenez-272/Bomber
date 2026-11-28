from django.contrib import admin
from .models import ComandoChatbot, EspecialidadVoluntario, FacilitadorCapacitacion, GuiaChatbot


@admin.register(EspecialidadVoluntario)
class EspecialidadVoluntarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'orden', 'activa')
    list_filter = ('activa',)
    search_fields = ('nombre', 'slug')
    ordering = ('orden', 'nombre')


@admin.register(FacilitadorCapacitacion)
class FacilitadorCapacitacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'activo')
    list_filter = ('tipo', 'activo')
    search_fields = ('nombre',)
    ordering = ('tipo', 'nombre')


@admin.register(GuiaChatbot)
class GuiaChatbotAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'modulo', 'prioridad', 'activo')
    list_filter = ('modulo', 'activo')
    search_fields = ('titulo', 'palabras_clave', 'pasos')
    ordering = ('-prioridad', 'titulo')


@admin.register(ComandoChatbot)
class ComandoChatbotAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'handler', 'modulo_requerido', 'prioridad', 'activo')
    list_filter = ('handler', 'modulo_requerido', 'activo')
    search_fields = ('nombre', 'palabras_clave')
    ordering = ('-prioridad', 'nombre')
