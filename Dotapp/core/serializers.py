from rest_framework import serializers
from core.models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id_usuario', 'nombre', 'apellido', 'correo', 'rol']
        read_only_fields = ['rol']  # El rol será siempre "aprendiz" al registrarse
