"""
Vistas para la aplicación de Aprendiz.

Este módulo contiene todas las vistas relacionadas con las funcionalidades
disponibles para los usuarios con rol de aprendiz, incluyendo:
- Gestión de perfil
- Creación y gestión de solicitudes
- Historial de solicitudes
- Borradores de solicitudes
"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from core.models import Solicitud, Producto, Borrador
from django.core.mail import EmailMultiAlternatives

from django.core.mail import EmailMessage
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from io import BytesIO
import imgkit
from PIL import Image, ImageDraw, ImageFont   # solo si la usas para otra cosa
from core.models import Solicitud, Producto, Borrador, TipoProducto, Talla, Color, CentroFormacion, Programa





@login_required
def bienvenido(request):
    """
    Vista de bienvenida para el aprendiz.
    
    Muestra una página de bienvenida después del login.
    
    Args:
        request: Objeto HttpRequest del usuario autenticado
        
    Returns:
        HttpResponse: Renderiza la página de bienvenida
    """
    return render(request, 'aprendiz/bienvenido.html')


@login_required
def principal(request):
    """
    Vista principal del panel del aprendiz.
    
    Muestra el dashboard principal con información del usuario.
    
    Args:
        request: Objeto HttpRequest del usuario autenticado
        
    Returns:
        HttpResponse: Renderiza el panel principal del aprendiz
    """
    return render(request, "aprendiz/principal.html", {
        "usuario": request.user
    })


@login_required
def logout_view(request):
    """
    Vista para cerrar sesión del usuario.
    
    Cierra la sesión del usuario actual y redirige al login.
    
    Args:
        request: Objeto HttpRequest
        
    Returns:
        HttpResponseRedirect: Redirige a la página de login
    """
    logout(request)
    return redirect("login")


@login_required
def perfil(request):
    """
    Vista para mostrar el perfil del aprendiz.
    
    Muestra la información del perfil del usuario autenticado.
    
    Args:
        request: Objeto HttpRequest del usuario autenticado
        
    Returns:
        HttpResponse: Renderiza la página de perfil
    """
    return render(request, "aprendiz/perfil.html", {
        "usuario": request.user
    })


@login_required
def actualizar_perfil(request):
    """
    Vista para actualizar el perfil del aprendiz.
    
    Permite al usuario actualizar su nombre, apellido y correo electrónico.
    
    Args:
        request: Objeto HttpRequest con los datos del formulario
        
    Returns:
        HttpResponse: Renderiza la página de perfil o redirige después de actualizar
    """
    usuario = request.user

    if request.method == 'POST':
        # Obtener los datos del formulario
        nuevo_nombre = request.POST.get('nombre')
        nuevo_apellido = request.POST.get('apellido')
        nuevo_correo = request.POST.get('correo')

        # Validar y actualizar los campos si existen
        if nuevo_nombre:
            usuario.nombre = nuevo_nombre
        if nuevo_apellido:
            usuario.apellido = nuevo_apellido
        if nuevo_correo:
            usuario.correo = nuevo_correo

        # Guardar los cambios en la base de datos
        usuario.save()

        # Mostrar mensaje de éxito
        messages.success(request, 'Perfil actualizado correctamente.')

        # Redireccionar a la página de perfil después de guardar
        return redirect('perfil-aprendiz')

    # Si la solicitud no es POST, simplemente renderiza la plantilla de perfil
    return render(request, 'perfil.html', {'usuario': usuario})


@login_required
def solicitud_uniforme(request):
    """
    Vista para crear una nueva solicitud de uniforme.
    
    Muestra el formulario de creación de solicitud con todos los productos
    disponibles, tipos, tallas, colores, centros y programas. Si el usuario
    tiene un borrador guardado, lo carga automáticamente.
    
    Args:
        request: Objeto HttpRequest del usuario autenticado
        
    Returns:
        HttpResponse: Renderiza el formulario de creación de solicitud
    """
    borrador = Borrador.objects.filter(aprendiz=request.user).first()
    productos = Producto.objects.filter(stock__gte=1).order_by('-stock')
    TipoProductos = TipoProducto.objects.all()
    Tallas = Talla.objects.all()
    Colores = Color.objects.all()
    Centros = CentroFormacion.objects.all()
    programas = Programa.objects.all()
    return render(request, 'aprendiz/creacion_solicitud.html', {
        "productos": productos,
        "tipos": TipoProductos,
        "tallas": Tallas,
        "colores": Colores,
        "borrador": borrador,
        "centros": Centros,
        "programas": programas
    })


def ajax_programas_por_centro(request):
    """
    Vista AJAX para obtener programas filtrados por centro de formación.
    
    Retorna una lista JSON de programas que pertenecen al centro especificado.
    Utilizada para cargar dinámicamente los programas en el formulario.
    
    Args:
        request: Objeto HttpRequest con el parámetro centro_id
        
    Returns:
        JsonResponse: Lista de programas en formato JSON
    """
    centro_id = request.GET.get("centro_id")
    programas = []
    if centro_id:
        programas = Programa.objects.filter(centro_id=centro_id).values("id_programa", "nombre")
    return JsonResponse({"programas": list(programas)})


'''
@login_required
def crear_solicitud(request):
    if request.method == "POST":
        # --- procesas los datos del formulario ---
        tipo_str = request.POST.get("tipo")
        talla_str = request.POST.get("talla")
        color_str = request.POST.get("color")
        cantidad = int(request.POST.get("cantidad") or 0)
        centro_id = request.POST.get("centro")
        programa_id = request.POST.get("programa")
        ficha = int(request.POST.get("ficha") or 0)
        detalles = request.POST.get("detalles") or ""

        # --- obtener objetos relacionados ---
        tipo_obj = TipoProducto.objects.filter(nombre=tipo_str).first()
        talla_obj = Talla.objects.filter(nombre=talla_str).first()
        color_obj = Color.objects.filter(nombre=color_str).first()
        centro_obj = CentroFormacion.objects.filter(id_centro=centro_id).first() if centro_id else None
        programa_obj = Programa.objects.filter(id_programa=programa_id).first() if programa_id else None

        if not tipo_obj or not talla_obj or not color_obj or not centro_obj or not programa_obj:
            messages.warning(request, "Faltan datos o datos inválidos.")
            return redirect("solicitud-uniforme")

        producto = Producto.objects.filter(tipo=tipo_obj, talla=talla_obj, color=color_obj).first()
        if not producto:
            messages.warning(request, "El producto seleccionado no está disponible.")
            return redirect("solicitud-uniforme")

        if cantidad > producto.stock:
            messages.warning(request, f"No hay suficiente stock. Solo queda {producto.stock} unidad{'es' if producto.stock != 1 else ''}.")
            return redirect("solicitud-uniforme")

        # --- crear solicitud ---
        solicitud = Solicitud.objects.create(
            id_aprendiz=request.user,
            tipo=tipo_obj.nombre,
            talla=talla_obj.nombre,
            color=color_obj.nombre,
            cantidad=cantidad,
            detalles_adicionales=detalles,
            centro_formacion=centro_obj.nombre,
            programa=programa_obj.nombre,
            ficha=ficha,
            estado_solicitud="pendiente",
            id_producto=producto
        )


        # --- eliminar borrador ---
        Borrador.objects.filter(aprendiz=request.user).delete()

        messages.success(request, "Solicitud creada exitosamente")
        return redirect("historial-solicitudes")

    return redirect("solicitud-uniforme")

'''

@login_required
def crear_solicitud(request):
    """
    Vista para crear una nueva solicitud de uniforme.
    
    Procesa el formulario de solicitud, valida los datos, verifica el stock
    disponible y crea la solicitud. Si la solicitud se crea exitosamente,
    elimina cualquier borrador guardado del usuario.
    
    Args:
        request: Objeto HttpRequest con los datos del formulario
        
    Returns:
        HttpResponseRedirect: Redirige al historial de solicitudes o al formulario
    """
    if request.method == "POST":
        # Procesar datos del formulario
        tipo_str = request.POST.get("tipo")
        talla_str = request.POST.get("talla")
        color_str = request.POST.get("color")
        cantidad = int(request.POST.get("cantidad") or 0)
        centro_id = request.POST.get("centro")
        programa_id = request.POST.get("programa")
        ficha = int(request.POST.get("ficha") or 0)
        detalles = request.POST.get("detalles") or ""

        # Obtener objetos relacionados
        tipo_obj = TipoProducto.objects.filter(nombre=tipo_str).first()
        talla_obj = Talla.objects.filter(nombre=talla_str).first()
        color_obj = Color.objects.filter(nombre=color_str).first()
        centro_obj = CentroFormacion.objects.filter(id_centro=centro_id).first() if centro_id else None
        programa_obj = Programa.objects.filter(id_programa=programa_id).first() if programa_id else None

        # Validaciones
        if not all([tipo_obj, talla_obj, color_obj, centro_obj, programa_obj]):
            messages.warning(request, "Faltan datos o algunos son inválidos.")
            return redirect("solicitud-uniforme")

        # Buscar producto correspondiente
        producto = Producto.objects.filter(tipo=tipo_obj, talla=talla_obj, color=color_obj).first()
        if not producto:
            messages.warning(request, "El producto seleccionado no está disponible.")
            return redirect("solicitud-uniforme")

        if cantidad > producto.stock:
            messages.warning(request, f"No hay suficiente stock. Solo quedan {producto.stock} unidad(es).")
            return redirect("solicitud-uniforme")

        # Crear solicitud
        solicitud = Solicitud.objects.create(
            id_aprendiz=request.user,
            tipo=tipo_obj,
            talla=talla_obj,
            color=color_obj,
            cantidad=cantidad,
            detalles_adicionales=detalles,
            centro_formacion=centro_obj,
            programa=programa_obj,
            ficha=ficha,
            estado_solicitud="pendiente",
            id_producto=producto
        )

        # Eliminar borrador si existe
        Borrador.objects.filter(aprendiz=request.user).delete()

        messages.success(request, "Solicitud creada exitosamente.")
        return redirect("historial-solicitudes")

    # Si no es POST, redirigir al formulario
    return redirect("solicitud-uniforme")





@login_required
def guardar_borrador(request):
    """
    Vista para guardar un borrador de solicitud.
    
    Permite al usuario guardar una solicitud incompleta para completarla
    más tarde. Solo se puede tener un borrador por usuario a la vez.
    
    Args:
        request: Objeto HttpRequest con los datos del formulario
        
    Returns:
        HttpResponseRedirect: Redirige al formulario de solicitud
    """
    if request.method != "POST":
        return redirect("solicitud-uniforme")

    centro = CentroFormacion.objects.filter(id_centro=request.POST.get("centro")).first() if request.POST.get("centro") else None
    programa = Programa.objects.filter(id_programa=request.POST.get("programa")).first() if request.POST.get("programa") else None

    Borrador.objects.update_or_create(
        aprendiz=request.user,
        defaults={
            "tipo": request.POST.get("tipo") or "",
            "talla": request.POST.get("talla") or "",
            "color": request.POST.get("color") or "",
            "cantidad": int(request.POST.get("cantidad") or 0),
            "centro": centro,
            "programa": programa,
            "ficha": int(request.POST.get("ficha") or 0),
            "detalles": request.POST.get("detalles") or "",
        }
    )
    messages.info(request, "Borrador guardado ✅")
    return redirect("solicitud-uniforme")


@login_required
def historial_solicitudes(request):
    """
    Vista para mostrar el historial de solicitudes del aprendiz.
    
    Muestra todas las solicitudes realizadas por el usuario autenticado.
    
    Args:
        request: Objeto HttpRequest del usuario autenticado
        
    Returns:
        HttpResponse: Renderiza el historial de solicitudes
    """
    solicitudes = Solicitud.objects.filter(id_aprendiz=request.user)
    return render(request, "aprendiz/historial_solicitudes.html", {
        "solicitudes": solicitudes,
    })


@login_required
def cancelar_solicitud(request, solicitud_id):
    """
    Vista para cancelar una solicitud pendiente.
    
    Permite al aprendiz cancelar una solicitud que está en estado "pendiente".
    Al cancelar, se envía un correo de notificación al aprendiz y se devuelve
    el stock al inventario.
    
    Args:
        request: Objeto HttpRequest del usuario autenticado
        solicitud_id: ID de la solicitud a cancelar
        
    Returns:
        HttpResponseRedirect: Redirige al historial de solicitudes
    """
    solicitud = get_object_or_404(Solicitud, id_solicitud=solicitud_id, id_aprendiz=request.user)

    if solicitud.estado_solicitud == "pendiente":
        solicitud.estado_solicitud = "cancelada"
        solicitud.save()

    text_content = (
        f"Hola {solicitud.id_aprendiz.get_full_name() or solicitud.id_aprendiz.username},\n\n"
        f"Tu solicitud con el ID: #{solicitud.id_solicitud} ha sido cancelada.\n"
        f"Si deseas hacer un nuevo pedido, créalo desde nuestro sitio web.\n\n"
        f"https://joan2004s.pythonanywhere.com/\n\n"
        f"Saludos,\nEl equipo de Dotapp"
    )

    html_content = f"""
    <html>
    <body style="font-family:Arial,Helvetica,sans-serif; background:#f7f7f7; padding:20px;">
        <div style="max-width:600px; margin:auto; background:white; border-radius:10px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,.1);">
            <div style="padding:20px;">
                Hola {solicitud.id_aprendiz.get_full_name() or solicitud.id_aprendiz.username},<br><br>
                Tu solicitud con el ID: #{solicitud.id_solicitud} ha sido cancelada.<br>
                Si deseas hacer un nuevo pedido, créalo desde nuestro sitio web.<br><br>
                <a href="https://joan2004s.pythonanywhere.com/">Dotapp</a><br><br>
                Saludos,<br>El equipo de Dotapp
            </div>
        </div>
    </body>
    </html>
    """

    msg = EmailMultiAlternatives(
        'Solicitud cancelada - Dotapp',
        text_content,
        'dotappsena@gmail.com',
        [solicitud.id_aprendiz.correo],
    )
    msg.attach_alternative(html_content, "text/html")

    # ⚡ Esto hará que Django muestre el error completo en pantalla
    msg.send(fail_silently=False)

    return redirect("historial-solicitudes")

