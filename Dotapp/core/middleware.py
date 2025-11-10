"""
Middleware personalizado para el sistema DotApp SENA.

Este módulo contiene middleware para guardar templates y manejar excepciones
de manera amigable para el usuario.
"""

from django.contrib import messages
from django.shortcuts import render, redirect


class SaveLastTemplateMiddleware:
    """
    Middleware para guardar el nombre del último template renderizado.
    
    Almacena el nombre del template en el objeto request para que pueda
    ser utilizado por otros middleware o vistas en caso de errores.
    """
    
    def __init__(self, get_response):
        """
        Inicializa el middleware.
        
        Args:
            get_response: Función que procesa la solicitud y retorna la respuesta
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Procesa la solicitud y guarda el template si está disponible.
        
        Args:
            request: Objeto HttpRequest
            
        Returns:
            HttpResponse: Respuesta procesada
        """
        response = self.get_response(request)
        if hasattr(response, 'template_name') and response.template_name:
            request._last_template = response.template_name
        return response


class AmigableExceptionMiddleware:
    """
    Middleware para manejar excepciones de manera amigable.
    
    Captura excepciones no manejadas y redirige al usuario a una página
    apropiada en lugar de mostrar un error técnico.
    """
    
    def __init__(self, get_response):
        """
        Inicializa el middleware.
        
        Args:
            get_response: Función que procesa la solicitud y retorna la respuesta
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Procesa la solicitud normalmente.
        
        Args:
            request: Objeto HttpRequest
            
        Returns:
            HttpResponse: Respuesta procesada
        """
        return self.get_response(request)

    def process_exception(self, request, exception):
        """
        Procesa excepciones no manejadas y redirige al usuario.
        
        Intenta redirigir al usuario a una página apropiada:
        1. Si es una vista de token único, redirige al login
        2. Si hay un template guardado, lo renderiza
        3. En caso contrario, redirige al login
        
        Args:
            request: Objeto HttpRequest
            exception: Excepción que se produjo
            
        Returns:
            HttpResponse: Redirección o renderizado de template
        """
        messages.error(request, "En este momento no podemos procesar tu solicitud. Por favor, inténtalo de nuevo más tarde.")

        # Verificar si es una vista de token único
        if getattr(request, '_vista_de_token_unico', False):
            return redirect('login')

        # Intentar usar el template guardado
        template = getattr(request, '_last_template', None)
        if template:
            return render(request, template, {})

        # Fallback: redirigir al login
        return redirect('login')
    

