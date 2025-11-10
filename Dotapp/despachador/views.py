"""
Vistas para la aplicación de Despachador.

Este módulo contiene todas las vistas relacionadas con las funcionalidades
disponibles para los usuarios con rol de despachador, incluyendo:
- Visualización de solicitudes despachadas
- Marcado de solicitudes como entregadas
"""

from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from core.models import Solicitud
from django.contrib import messages


@login_required
def dashboard_despachador(request):
    """
    Vista del panel principal del despachador.
    
    Verifica que el usuario tenga rol de administrador o despachador.
    
    Args:
        request: Objeto HttpRequest del usuario autenticado
        
    Returns:
        HttpResponse: Renderiza el dashboard o redirige si no tiene permisos
    """
    if request.user.rol is None or request.user.rol.nombre_rol not in ["administrador", "despachador"]:
        return redirect(reverse("acceso_denegado"))
    return render(request, "despachador/dashboard_despachador.html")


@login_required
def solicitudes_pendientes(request):
    """
    Vista para mostrar las solicitudes despachadas pendientes de entrega.
    
    Muestra todas las solicitudes que están en estado "despachada",
    ordenadas por fecha de solicitud (más recientes primero).
    
    Args:
        request: Objeto HttpRequest del usuario autenticado
        
    Returns:
        HttpResponse: Renderiza la página de solicitudes pendientes
    """
    solicitudes = (
    Solicitud.objects
    .select_related("id_aprendiz", "id_producto")
    .exclude(estado_solicitud__in=["cancelada", "pendiente", "rechazada", "borrador", "entregada", "aprobada"])
    )

    # Ordenar por fecha de solicitud (más recientes primero)
    solicitudes = solicitudes.order_by("-fecha_solicitud")
    return render(request, 'despachador/Solicitudes_pendientes.html', {'solicitudes': solicitudes})


@login_required
def entregar_solicitud(request, solicitud_id):
    """
    Vista para marcar una solicitud como entregada.
    
    Cambia el estado de la solicitud de "despachada" a "entregada"
    y envía un correo de notificación al aprendiz confirmando la entrega.
    
    Args:
        request: Objeto HttpRequest del usuario autenticado
        solicitud_id: ID de la solicitud a marcar como entregada
        
    Returns:
        HttpResponseRedirect: Redirige a la página de solicitudes pendientes
    """
    solicitud = get_object_or_404(Solicitud, id_solicitud=solicitud_id)

    if solicitud.estado_solicitud == "despachada":
        solicitud.estado_solicitud = "entregada"
        solicitud.save()


    # Contenido texto del correo
    text_content = (
        f'Hola {solicitud.id_aprendiz.get_full_name() or solicitud.id_aprendiz.username},\n\n'
        f'Tu solicitud con el ID: #{solicitud.id_solicitud} ha sido ENTREGADA.\n'
        f'Gracias por usar Dotapp. ¡Esperamos verte pronto!\n\n'
        f"Si deseas hacer un nuevo pedido, créalo desde nuestro sitio web.\n\n"
        f'https://joan2004s.pythonanywhere.com/ \n\n'
        f'Muchas gracias por tu paciencia.\n\n'
        f'Saludos,\nEl equipo de Dotapp'
    )

    # Contenido HTML del correo
    html_content = f"""
    <html>
    <body style="font-family:Arial,Helvetica,sans-serif; background:#f7f7f7; padding:20px;">
        <div style="max-width:600px; margin:auto; background:white; border-radius:10px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,.1);">
            <div style="padding:20px;">
                Hola {solicitud.id_aprendiz.get_full_name() or solicitud.id_aprendiz.username},<br><br>
                Tu solicitud con el ID: #{solicitud.id_solicitud} ha sido ENTREGADA.<br>
                Si deseas hacer un nuevo pedido, créalo desde nuestro sitio web.<br><br>
                <a href="https://joan2004s.pythonanywhere.com/">Dotapp</a><br><br>
                Saludos,<br>El equipo de Dotapp
            </div>
        </div>
    </body>
    </html>
    """

    # Configurar el correo
    msg = EmailMultiAlternatives(
        'Solicitud entregada - Dotapp',
        text_content,
        'dotappsena@gmail.com',
        [solicitud.id_aprendiz.correo],
    )

    # Adjuntar el contenido HTML
    msg.attach_alternative(html_content, "text/html")

    # 🚀 Enviar el correo
    msg.send(fail_silently=False)

    messages.success(request, "Solicitud entregada exitosamente.")

    return redirect("solicitudes_pendientes")