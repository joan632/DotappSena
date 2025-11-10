"""
Señales (signals) de Django para el sistema DotApp SENA.

Este módulo contiene señales que se ejecutan automáticamente
en ciertos eventos del sistema, como después de las migraciones.
"""

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from core.models import Rol


@receiver(post_migrate)
def crear_roles_iniciales(sender, **kwargs):
    """
    Crea los roles iniciales del sistema después de ejecutar migraciones.
    
    Esta función se ejecuta automáticamente después de cada migración
    y asegura que los roles básicos del sistema existan en la base de datos:
    - aprendiz
    - administrador
    - despachador
    - almacenista
    
    Args:
        sender: Modelo o aplicación que disparó la señal
        **kwargs: Argumentos adicionales de la señal
    """
    # Solo ejecutar para la app "core"
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
