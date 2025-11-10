"""
Generador de tokens con expiración para recuperación de contraseña.

Este módulo proporciona un generador de tokens personalizado que expira
después de un tiempo determinado (15 minutos por defecto).
"""

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from datetime import datetime, timedelta


class ExpiringTokenGenerator(PasswordResetTokenGenerator):
    """
    Generador de tokens de recuperación de contraseña con expiración.
    
    Los tokens generados por esta clase expiran después de 15 minutos
    para mayor seguridad en el proceso de recuperación de contraseña.
    """
    
    def _make_hash_value(self, user, timestamp):
        """
        Genera el valor hash para el token basado en el usuario y timestamp.
        
        Args:
            user: Instancia del usuario
            timestamp: Timestamp de creación del token
            
        Returns:
            str: Valor hash combinado del usuario y timestamp
        """
        return str(user.pk) + str(timestamp) + str(user.is_active)

EPOCH = datetime(2001, 1, 1)  # Base usada por Django para timestamps


def check_token(self, user, token):
    """
    Verifica si un token es válido y no ha expirado.
    
    Args:
        user: Instancia del usuario
        token: Token a verificar
        
    Returns:
        bool: True si el token es válido y no ha expirado, False en caso contrario
    """
    if not super().check_token(user, token):
        return False

    # Extraer timestamp del token
    ts_b36 = token.split("-")[1] if "-" in token else None
    if ts_b36 is None:
        return False

    try:
        ts_int = int(ts_b36, 36)
    except ValueError:
        return False

    # Convertir el timestamp base36 a datetime válido
    token_time = EPOCH + timedelta(seconds=ts_int)

    # Verificar expiración (15 minutos)
    if datetime.now() > token_time + timedelta(minutes=15):
        return False

    return True


# Instancia global del generador de tokens
expiring_token_generator = ExpiringTokenGenerator()