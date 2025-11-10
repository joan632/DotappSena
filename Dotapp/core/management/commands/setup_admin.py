"""
Comando de gestión para crear el usuario administrador inicial.

Este comando permite crear automáticamente el primer superusuario
del sistema usando las credenciales definidas en variables de entorno.
"""

import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Rol


class Command(BaseCommand):
    """
    Comando para crear un usuario administrador inicial.
    
    Lee las credenciales desde variables de entorno (ADMIN_EMAIL y ADMIN_PASSWORD)
    y crea un superusuario si no existe uno en el sistema.
    """
    
    help = 'Crea un usuario administrador inicial si no existe'

    def handle(self, *args, **options):
        """
        Ejecuta el comando para crear el superusuario.
        
        Verifica si ya existe un superusuario. Si no existe, crea uno nuevo
        usando las credenciales de las variables de entorno.
        
        Args:
            *args: Argumentos posicionales
            **options: Opciones del comando
        """
        User = get_user_model()
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')

        # Verificar si ya existe un superusuario
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.WARNING("El superusuario ya existe. No se creará uno nuevo."))
            return

        self.stdout.write("Detectada la primera ejecución. Creando usuario administrador...")

        # Verificar que las credenciales estén configuradas
        if not admin_email or not admin_password:
            self.stdout.write(self.style.ERROR("Las credenciales del superusuario (ADMIN_EMAIL y ADMIN_PASSWORD) no están configuradas en el archivo .env."))
            return

        try:
            # Crear el superusuario con rol de Administrador
            user = User.objects.create_superuser(
                nombre="administrador",
                apellido="administrador",
                correo=admin_email,
                password=admin_password
            )
            
            # Notificar éxito
            self.stdout.write(self.style.SUCCESS(f"Usuario administrador '{user.correo}' creado exitosamente."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al crear el superusuario: {e}"))