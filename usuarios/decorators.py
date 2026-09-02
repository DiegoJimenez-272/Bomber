from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

def admin_required(view_func):
    """
    Decorador para restringir el acceso a vistas que requieren privilegios de administración (is_staff o is_superuser).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'No tienes privilegios de administración para acceder a este recurso.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def permiso_requerido(permiso_attr):
    """
    Decorador para verificar permisos específicos del rol del usuario (ej: 'ver_inventario', 'editar_documentacion').
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Superusuarios se saltan la verificación de roles
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            rol = getattr(request.user, 'rol', None)
            if not rol or not getattr(rol, permiso_attr, False):
                messages.error(request, 'No tienes permisos suficientes para realizar esta acción.')
                return redirect('dashboard')
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def pertenencia_compania(user, compania_target):
    """
    Verifica si el usuario tiene acceso a un recurso según su compañía.
    Superusuarios tienen acceso global.
    """
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if compania_target is None:
        return True
    return user.compania == compania_target
