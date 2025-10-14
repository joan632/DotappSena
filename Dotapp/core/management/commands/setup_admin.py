# C:\DotappSENA\Dotapp\core\management\commands\setup_admin.py
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Rol # Importa el modelo Rol

class Command(BaseCommand):
    help = 'Crea un usuario administrador inicial si no existe'

    def handle(self, *args, **options):
        User = get_user_model()
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')

        # 1. El Sistema detecta que es la primera ejecución.
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.WARNING("El superusuario ya existe. No se creará uno nuevo."))
            return

        self.stdout.write("Detectada la primera ejecución. Creando usuario administrador...")

        # 2. Obtiene las credenciales
        if not admin_email or not admin_password:
            self.stdout.write(self.style.ERROR("Las credenciales del superusuario (ADMIN_EMAIL y ADMIN_PASSWORD) no están configuradas en el archivo .env."))
            return

        try:
            # 3. Genera el usuario con rol de Administrador.
            #    Se usa "administrador" como nombre y apellido, según tu indicación.
            user = User.objects.create_superuser(
                nombre="administrador",
                apellido="administrador",
                correo=admin_email,
                password=admin_password
            )
            # 4. Guarda el usuario en la base de datos (create_superuser ya lo hace).
            
            # 5. Notifica en consola/log
            self.stdout.write(self.style.SUCCESS(f"Usuario administrador '{user.correo}' creado exitosamente."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error al crear el superusuario: {e}"))