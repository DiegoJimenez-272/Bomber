from .decorators import pertenencia_compania


def puede_editar_inventario(user):
    rol = getattr(user, 'rol', None)
    return bool(user.is_superuser or (rol and rol.editar_inventario))


def puede_gestionar_inventario_global(user):
    rol = getattr(user, 'rol', None)
    return bool(
        user.is_superuser
        or (rol and rol.editar_inventario and rol.gestionar_inventario_todas_companias)
    )


def puede_acceder_inventario_compania(user, compania):
    return puede_gestionar_inventario_global(user) or (
        compania is not None and pertenencia_compania(user, compania)
    )
