from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from core.models import Usuario
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages

User = get_user_model()

#vista para registro
def registro_aprendiz(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        correo = request.POST.get('correo')
        password = request.POST.get('password')
        confirmar_password = request.POST.get('confirmar-contrasena')

        # Validaciones previas sin tocar DB
        if password != confirmar_password:
            messages.error(request, "Las contraseñas no coinciden.")
            return render(request, 'core/registro.html')

        if len(password) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
            return render(request, 'core/registro.html')

        try:
            if Usuario.objects.filter(correo=correo).exists():
                messages.error(request, "Este correo ya está registrado.")
                return redirect('login')

            Usuario.objects.create_user(
                nombre=nombre,
                apellido=apellido,
                correo=correo,
                password=password
            )
        except Exception:
            messages.error(request, "Error, intente nuevamente.")
            return render(request, 'core/registro.html')

        messages.success(request, "¡Registro exitoso! Ya puedes iniciar sesión.")
        return render(request, 'core/login.html')

    return render(request, 'core/registro.html')

#vista para login
def login_view(request):
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



#solicitud de correo
# core/views.py
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
# 1) Vista para pedir correo y enviar email
def password_reset_request(request):
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

        send_mail(
            'Recupera tu contraseña',
            f'Hola,\n\nRecibimos una solicitud para restablecer tu contraseña en DotAppSena. '
            f'Para crear una nueva contraseña visita el siguiente enlace (válido 15 minutos):\n\n'
            f'{reset_url}\n\n'
            f'Si no solicitaste este cambio, simplemente ignora este correo.\n\n'
            f'Saludos,\nEl equipo de Dotapp',
            'dotappsena@gmail.com',
            [email],
            fail_silently=False,
        )
        return JsonResponse({"status": "ok"})

    # GET → muestra el formulario para poner el correo
    return render(request, "core/password_reset.html", {"status": "email"})


# 2) Vista para confirmar y cambiar contraseña
def password_reset_confirm(request, uidb64, token):
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
    
#vista para dashboard de administracion
@login_required
def dashboard_admin(request):
    return render(request, 'core/dashboard_admin.html')

#vista para acceso denegado
def acceso_denegado(request):
    return render(request, 'core/acceso_denegado.html')


#vista para redireccionar cuando falla el csrf
def csrf_error_redirect(request, reason=""):
    """
    Redirige a la página de inicio cuando falla el CSRF.
    """
    return redirect("login")


#vistas para manejo de errores

def error_view(request, exception=None, status_code=500, message="Ocurrió un error."):
    return render(request, 'core/error.html', {
        'status_code': status_code,
        'message': message
    }, status=status_code)

def error_404_view(request, exception):
    return error_view(request, exception, status_code=404, message="La página que estás buscando no existe.")

def error_500_view(request):
    return error_view(request, status_code=500, message="Error interno del servidor.")

def error_403_view(request, exception):
    return error_view(request, exception, status_code=403, message="No tienes permiso para acceder a esta página.")

def error_400_view(request, exception):
    return error_view(request, exception, status_code=400, message="Solicitud incorrecta.")
