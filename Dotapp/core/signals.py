from django.db.models.signals import post_migrate
from django.dispatch import receiver
from core.models import Rol

@receiver(post_migrate)
def crear_roles_iniciales(sender, **kwargs):
    # Solo correr para tu app "core"
    if sender.name != 'core':
        return

    roles_iniciales = ['aprendiz', 'administrador', 'despachador', 'almacenista']
    creados = []

    for rol_nombre in roles_iniciales:
        rol, creado = Rol.objects.get_or_create(nombre_rol=rol_nombre)
        if creado:
            creados.append(rol_nombre)

    if creados:
        print(f"Roles creados exitosamente: {', '.join(creados)}")
    else:
        print("Todos los roles iniciales ya existían. No se creó ninguno.")
