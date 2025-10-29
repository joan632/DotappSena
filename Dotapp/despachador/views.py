from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from core.models import Solicitud
from django.contrib import messages
# Create your views here.

@login_required
def dashboard_despachador(request):
    if request.user.rol is None or request.user.rol.nombre_rol not in ["administrador", "despachador"]:
        return redirect(reverse("acceso_denegado"))
    return render(request, "despachador/dashboard_despachador.html")


@login_required
def solicitudes_pendientes(request):
    solicitudes = (
    Solicitud.objects
    .select_related("id_aprendiz", "id_producto")
    .exclude(estado_solicitud__in=["cancelada", "pendiente", "rechazada", "borrador", "entregada", "aprobada"])
    )

    # ordenar por fecha de solicitud
    solicitudes = solicitudes.order_by("-fecha_solicitud")
    return render(request, 'despachador/Solicitudes_pendientes.html', {'solicitudes': solicitudes})

@login_required
def entregar_solicitud(request, solicitud_id):
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
        'e.lfc.joan.vargas@cali.edu.co',
        [solicitud.id_aprendiz.correo],
    )

    # Adjuntar el contenido HTML
    msg.attach_alternative(html_content, "text/html")

    # 🚀 Enviar el correo
    msg.send(fail_silently=False)

    messages.success(request, "Solicitud entregada exitosamente.")

    return redirect("solicitudes_pendientes")