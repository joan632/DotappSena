"""
Vistas principales del sistema DotApp SENA.

Este módulo contiene las vistas para autenticación, registro de usuarios,
recuperación de contraseña y manejo de errores.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.models import Usuario
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

User = get_user_model()


def registro_aprendiz(request):
    """
    Vista para el registro de nuevos aprendices.
    
    Permite a los usuarios crear una cuenta nueva en el sistema.
    Valida que las contraseñas coincidan, tengan al menos 8 caracteres,
    y que el correo tenga un formato válido y no esté ya registrado.
    
    Args:
        request: Objeto HttpRequest con los datos del formulario
        
    Returns:
        HttpResponse: Renderiza la plantilla de registro o login según el caso
    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        password = request.POST.get('password')
        confirmar_password = request.POST.get('confirmar-contrasena')

        # Validar que las contraseñas coincidan
        if password != confirmar_password:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'core/Registro.html')

        # Validar longitud mínima de contraseña
        if len(password) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
            return render(request, 'core/Registro.html')

        # Validar formato de correo
        try:
            validate_email(correo)
        except ValidationError:
            messages.error(request, "El correo ingresado no tiene un formato válido.")
            return render(request, 'core/Registro.html')

        # Verificar si el correo ya existe
        if Usuario.objects.filter(correo=correo).exists():
            messages.error(request, "Este correo ya está registrado.")
            return redirect('login')

        # Crear usuario
        try:
            Usuario.objects.create_user(
                nombre=nombre,
                apellido=apellido,
                correo=correo,
                password=password
            )
        except Exception:
            messages.error(request, "Error, intente nuevamente.")
            return render(request, 'core/Registro.html')

        messages.success(request, "¡Registro exitoso! Ya puedes iniciar sesión.")
        return render(request, 'core/login.html')

    return render(request, 'core/Registro.html')


def login_view(request):
    """
    Vista para el inicio de sesión de usuarios.
    
    Autentica al usuario usando correo y contraseña, y redirige según su rol:
    - Administrador, Despachador, Almacenista: Dashboard de administración
    - Aprendiz: Página de bienvenida del aprendiz
    
    Args:
        request: Objeto HttpRequest con las credenciales del usuario
        
    Returns:
        HttpResponse: Renderiza la plantilla de login o redirige según el rol
    """
    if request.method == 'POST':
        correo = request.POST.get('correo')
        password = request.POST.get('password')

        try:
            usuario = authenticate(request, username=correo, password=password)
        except Exception:
            messages.error(request, "Error, intente nuevamente.")
            return render(request, 'core/login.html')

        if usuario is not None and usuario.is_active:
            login(request, usuario)
            roles_admin = ['administrador', 'despachador', 'almacenista']
            if usuario.rol.nombre_rol in roles_admin:
                return redirect('dashboard_admin')
            elif usuario.rol.nombre_rol == 'aprendiz':
                return redirect('bienvenido-aprendiz')
        else:
            messages.error(request, "Credenciales inválidas")

    return render(request, 'core/login.html')


def manual(request):
    """
    Vista para mostrar el manual de usuario.
    
    Args:
        request: Objeto HttpRequest
        
    Returns:
        HttpResponse: Renderiza la plantilla del manual de usuario
    """
    return render(request, 'core/manual_usuario.html')

import json
from django.http import JsonResponse
from django.shortcuts import render
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.forms import SetPasswordForm
from .models import Usuario
from .tokens import expiring_token_generator
from django.contrib.auth.tokens import PasswordResetTokenGenerator

expiring_token_generator = PasswordResetTokenGenerator()


def password_reset_request(request):
    """
    Vista para solicitar el restablecimiento de contraseña.
    
    Recibe el correo del usuario y envía un email con un enlace
    para restablecer la contraseña. El token tiene una validez de 15 minutos.
    
    Args:
        request: Objeto HttpRequest con el correo en el body (JSON)
        
    Returns:
        JsonResponse: Estado de la operación (ok o error)
        HttpResponse: Formulario para ingresar el correo (GET)
    """
    if request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")

        try:
            user = Usuario.objects.get(correo=email)
        except Usuario.DoesNotExist:
            return JsonResponse({"status": "error", "message": "El correo no existe en el sistema"})

        token = expiring_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = request.build_absolute_uri(
            reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        )

            # Contenido texto opcional del correo
        text_content = (
            f'Hola,\n\nRecibimos una solicitud para restablecer tu contraseña en DotAppSena. '
            f'Para crear una nueva contraseña visita el siguiente enlace (válido 15 minutos):\n\n'
            f'{reset_url}\n\n'
            f'Si no solicitaste este cambio, simplemente ignora este correo.\n\n'
            f'Saludos,\nEl equipo de Dotapp'
        )

        # Contenido HTML del correo
        html_content = f"""
        <html>
        <body style="font-family:Arial,Helvetica,sans-serif; background:#f7f7f7; padding:20px;">
            <div style="max-width:600px; margin:auto; background:white; border-radius:10px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,.1);">
                <div style="padding:20px;">
                    Hola,<br><br>
                    Recibimos una solicitud para restablecer tu contraseña en DotAppSena.<br>
                    Para crear una nueva contraseña visita el siguiente enlace (válido 15 minutos):<br><br>
                    <a href="{reset_url}">Restablecer contraseña</a><br><br>
                    Si no solicitaste este cambio, simplemente ignora este correo.<br><br>
                    <br>
                    Saludos,<br>El equipo de Dotapp
                </div>
            </div>
        </body>
        </html>
        """

        msg = EmailMultiAlternatives(
            'Recupera tu contraseña',
            text_content,
            'dotappsena@gmail.com',
            [email]
        )
        msg.attach_alternative(html_content, "text/html")

        msg.send(fail_silently=False)
        
        return JsonResponse({"status": "ok"})

    # GET: muestra el formulario para ingresar el correo
    return render(request, "core/password_reset.html", {"status": "email"})


def password_reset_confirm(request, uidb64, token):
    """
    Vista para confirmar y cambiar la contraseña del usuario.
    
    Valida el token y el UID proporcionados en el enlace de recuperación.
    Si son válidos, muestra un formulario para establecer la nueva contraseña.
    
    Args:
        request: Objeto HttpRequest
        uidb64: ID del usuario codificado en base64
        token: Token de restablecimiento de contraseña
        
    Returns:
        HttpResponse: Formulario para cambiar contraseña o mensaje de error
    """
    request._vista_de_token_unico = True  # Marca para el middleware
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, Usuario.DoesNotExist):
        user = None

    if user is not None and expiring_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return render(request, "core/password_reset.html", {
                    "status": "complete",
                    "message": "Tu contraseña ha sido actualizada con éxito."
                })
        else:
            form = SetPasswordForm(user)
        return render(request, "core/password_reset.html", {"status": "show_form", "form": form})

    return render(request, "core/password_reset.html", {
        "status": "error",
        "message": "El enlace no es válido o ha caducado."
    })

@login_required
def dashboard_admin(request):
    """
    Vista para el dashboard de administración.
    
    Panel principal para usuarios con roles de administrador, almacenista o despachador.
    Requiere autenticación.
    
    Args:
        request: Objeto HttpRequest del usuario autenticado
        
    Returns:
        HttpResponse: Renderiza el dashboard de administración
    """
    return render(request, 'core/dashboard_admin.html')


def acceso_denegado(request):
    """
    Vista para mostrar mensaje de acceso denegado.
    
    Se muestra cuando un usuario intenta acceder a una página
    para la cual no tiene permisos.
    
    Args:
        request: Objeto HttpRequest
        
    Returns:
        HttpResponse: Renderiza la página de acceso denegado
    """
    return render(request, 'core/acceso_denegado.html')


def csrf_error_redirect(request, reason=""):
    """
    Redirige a la página de inicio cuando falla la validación CSRF.
    
    Args:
        request: Objeto HttpRequest
        reason: Razón del fallo CSRF (opcional)
        
    Returns:
        HttpResponseRedirect: Redirige a la página de login
    """
    return redirect("login")


def error_view(request, exception=None, status_code=500, message="Ocurrió un error."):
    """
    Vista genérica para manejo de errores HTTP.
    
    Args:
        request: Objeto HttpRequest
        exception: Excepción que causó el error (opcional)
        status_code: Código de estado HTTP
        message: Mensaje de error a mostrar
        
    Returns:
        HttpResponse: Renderiza la plantilla de error con el código de estado
    """
    return render(request, 'core/error.html', {
        'status_code': status_code,
        'message': message
    }, status=status_code)


def error_404_view(request, exception):
    """
    Vista para manejar errores 404 (Página no encontrada).
    
    Args:
        request: Objeto HttpRequest
        exception: Excepción que causó el error
        
    Returns:
        HttpResponse: Renderiza la plantilla de error 404
    """
    return error_view(request, exception, status_code=404, message="La página que estás buscando no existe.")


def error_500_view(request):
    """
    Vista para manejar errores 500 (Error interno del servidor).
    
    Args:
        request: Objeto HttpRequest
        
    Returns:
        HttpResponse: Renderiza la plantilla de error 500
    """
    return error_view(request, status_code=500, message="Error interno del servidor.")


def error_403_view(request, exception):
    """
    Vista para manejar errores 403 (Acceso prohibido).
    
    Args:
        request: Objeto HttpRequest
        exception: Excepción que causó el error
        
    Returns:
        HttpResponse: Renderiza la plantilla de error 403
    """
    return error_view(request, exception, status_code=403, message="No tienes permiso para acceder a esta página.")


def error_400_view(request, exception):
    """
    Vista para manejar errores 400 (Solicitud incorrecta).
    
    Args:
        request: Objeto HttpRequest
        exception: Excepción que causó el error
        
    Returns:
        HttpResponse: Renderiza la plantilla de error 400
    """
    return error_view(request, exception, status_code=400, message="Solicitud incorrecta.")
