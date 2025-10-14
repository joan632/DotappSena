#vista para recuperar contraseña
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from datetime import datetime, timedelta

class ExpiringTokenGenerator(PasswordResetTokenGenerator):
    """
    Token de recuperación de contraseña válido 15 minutos.
    """
    def _make_hash_value(self, user, timestamp):
        return str(user.pk) + str(timestamp) + str(user.is_active)

EPOCH = datetime(2001, 1, 1)  # Base usada por Django

def check_token(self, user, token):
    if not super().check_token(user, token):
        return False

    # Extraer timestamp
    ts_b36 = token.split("-")[1] if "-" in token else None
    if ts_b36 is None:
        return False

    try:
        ts_int = int(ts_b36, 36)
    except ValueError:
        return False

    # Convertir el timestamp base36 a datetime válido
    token_time = EPOCH + timedelta(seconds=ts_int)

    # Verificar expiración (ej: 15 minutos)
    if datetime.now() > token_time + timedelta(minutes=1):
        return False

    return True

# Instancia global
expiring_token_generator = ExpiringTokenGenerator()