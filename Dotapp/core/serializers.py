"""
Serializadores de Django REST Framework para el sistema DotApp SENA.

Este módulo contiene los serializadores que convierten los modelos
a formato JSON para la API REST.
"""

from rest_framework import serializers
from core.models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Usuario.
    
    Permite serializar y deserializar instancias del modelo Usuario
    para su uso en la API REST. El campo 'rol' es de solo lectura
    ya que se asigna automáticamente al crear un usuario.
    """
    
    class Meta:
        model = Usuario
        fields = ['id_usuario', 'nombre', 'apellido', 'correo', 'rol']
        read_only_fields = ['rol']  # El rol será siempre "aprendiz" al registrarse
