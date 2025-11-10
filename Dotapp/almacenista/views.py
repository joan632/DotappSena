"""
Vistas para la aplicación de Almacenista.

Este módulo contiene todas las vistas relacionadas con las funcionalidades
disponibles para los usuarios con rol de almacenista, incluyendo:
- Gestión de productos e inventario
- Aprobación y rechazo de solicitudes
- Gestión de tipos, tallas, colores, centros y programas
"""

import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Producto, Solicitud, TipoProducto, Talla, Color, CentroFormacion, Programa
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.urls import reverse
import pdfkit
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string

import json


# Configuración de wkhtmltopdf en PythonAnywhere
PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')


def generar_factura_pdf_bytes(solicitud):
    # Usar la ruta absoluta del archivo de la imagen
    producto_abs_path = solicitud.id_producto.imagen.path

    # Renderizar HTML con la ruta absoluta
    html_factura = render_to_string('core/factura.html', {
        's': solicitud,
        'total': solicitud.cantidad * solicitud.id_producto.precio,
        'producto_abs_path': producto_abs_path,
    })

    try:
        options = {
            'enable-local-file-access': '',
            'orientation': 'Landscape',
            'margin-top': '0mm',
            'margin-bottom': '0mm',
            'margin-left': '0mm',
            'margin-right': '0mm',
            'page-size': 'Letter',          # o 'A4', da igual
            'disable-smart-shrinking': '',  # evita que achique el contenido
            'zoom': '1.0',                  # asegura escala real
            'print-media-type': '',         # aplica los estilos @page y @media print
        }

        # Generar PDF en memoria
        pdf_bytes = pdfkit.from_string(html_factura, False, configuration=PDFKIT_CONFIG, options=options)
        return pdf_bytes

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e



        
@login_required
def dashboard_almacenista(request):
    """
    Vista del panel principal del almacenista.
    
    Verifica que el usuario tenga rol de administrador o almacenista.
    
    Args:
        request: Objeto HttpRequest del usuario autenticado
        
    Returns:
        HttpResponse: Renderiza el dashboard o redirige si no tiene permisos
    """
    if request.user.rol is None or request.user.rol.nombre_rol not in ["administrador", "almacenista"]:
        return redirect(reverse("acceso_denegado"))
    return render(request, "almacenista/dashboard_almacenista.html")


import json
from django.core.serializers.json import DjangoJSONEncoder

@login_required
def administrar_productos(request):
    """
    Vista para administrar productos del inventario.
    
    Muestra todos los productos con sus tipos, tallas, colores y stock disponible.
    Proporciona datos en formato JSON para uso con JavaScript.
    
    Args:
        request: Objeto HttpRequest del usuario autenticado
        
    Returns:
        HttpResponse: Renderiza la página de administración de productos
    """
    productos = Producto.objects.order_by('stock')
    tipos = list(TipoProducto.objects.all().values('id_tipo', 'nombre'))
    tallas = list(Talla.objects.all().values('id_talla', 'nombre'))
    colores = list(Color.objects.all().values('id_color', 'nombre'))

    return render(request, 'almacenista/administracion_productos.html', {
        'productos': productos,
        'tipos': TipoProducto.objects.all(),
        'tallas': Talla.objects.all(),
        'colores': Color.objects.all(),
        'MEDIA_URL': settings.MEDIA_URL,
        'tipos_json': json.dumps(tipos, cls=DjangoJSONEncoder),
        'tallas_json': json.dumps(tallas, cls=DjangoJSONEncoder),
        'colores_json': json.dumps(colores, cls=DjangoJSONEncoder),
    })


# 🟢 Agregar Centro de Formación
@login_required
def agregar_centro(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        if not nombre:
            messages.warning(request, "Ingresa un nombre de centro.")
            return redirect("gestion_palabras")

        nombre = nombre.title()
        centro, created = CentroFormacion.objects.get_or_create(nombre=nombre)
        if created:
            messages.success(request, f"Centro '{centro.nombre}' agregado correctamente.")
        else:
            messages.warning(request, f"El centro '{centro.nombre}' ya existe.")
        return redirect("gestion_palabras")
    else:
        messages.error(request, "Método no permitido.")
        return redirect("gestion_palabras")


# 🟢 Agregar Programa
@login_required
def agregar_programa(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        centro_id = request.POST.get("centro_id")

        if not nombre or not centro_id:
            messages.warning(request, "Ingresa todos los campos.")
            return redirect("gestion_palabras")

        try:
            centro = CentroFormacion.objects.get(id_centro=centro_id)
        except CentroFormacion.DoesNotExist:
            messages.error(request, "El centro seleccionado no existe.")
            return redirect("gestion_palabras")

        nombre = nombre.title()
        programa, created = Programa.objects.get_or_create(nombre=nombre, centro=centro)

        if created:
            messages.success(request, f"Programa '{programa.nombre}' agregado correctamente al centro '{centro.nombre}'.")
        else:
            messages.warning(request, f"El programa '{programa.nombre}' ya existe en '{centro.nombre}'.")

        return redirect("gestion_palabras")
    else:
        messages.error(request, "Método no permitido.")
        return redirect("gestion_palabras")


@csrf_exempt
def agregar_producto(request):
    """
    Vista para agregar un nuevo producto al inventario.
    
    Crea un nuevo producto con tipo, talla, color, precio, stock e imagen.
    Retorna una respuesta JSON con el estado de la operación.
    
    Args:
        request: Objeto HttpRequest con los datos del formulario (POST)
        
    Returns:
        JsonResponse: Estado de la operación (ok o error)
    """
    if request.method == 'POST':
        tipo_nombre = request.POST.get('tipo')
        talla_nombre = request.POST.get('talla')
        color_nombre = request.POST.get('color')
        precio = request.POST.get('precio')
        stock = request.POST.get('cantidad')
        imagen_file = request.FILES.get('imagen')

        if not all([tipo_nombre, talla_nombre, color_nombre, precio, stock]):
            return JsonResponse({'status': 'error', 'message': 'Faltan datos'}, status=400)

        # Crear o recuperar los objetos relacionados
        tipo_obj, _ = TipoProducto.objects.get_or_create(nombre=tipo_nombre)
        talla_obj, _ = Talla.objects.get_or_create(nombre=talla_nombre)
        color_obj, _ = Color.objects.get_or_create(nombre=color_nombre)

        # Guardar la imagen
        imagen_ruta = ''
        if imagen_file:
            carpeta = os.path.join(settings.MEDIA_ROOT, 'productos')
            os.makedirs(carpeta, exist_ok=True)
            ruta_completa = os.path.join(carpeta, imagen_file.name)
            with open(ruta_completa, 'wb+') as f:
                for chunk in imagen_file.chunks():
                    f.write(chunk)
            imagen_ruta = f'productos/{imagen_file.name}'

        producto = Producto.objects.create(
            tipo=tipo_obj,
            precio=precio,
            talla=talla_obj,
            color=color_obj,
            stock=stock,
            imagen=imagen_ruta,
            almacenista=request.user
        )

        return JsonResponse({'status': 'ok', 'producto_id': producto.id_producto})

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


#vista para configurar productos
from django.db.models import Value, CharField

@login_required
def config_productos(request):
    tipos = list(
        TipoProducto.objects.annotate(cat=Value('T', CharField()))
        .values('id_tipo', 'nombre', 'cat')
    )
    tallas = list(
        Talla.objects.annotate(cat=Value('L', CharField()))
        .values('id_talla', 'nombre', 'cat')
    )
    colores = list(
        Color.objects.annotate(cat=Value('C', CharField()))
        .values('id_color', 'nombre', 'cat')
    )
    return render(request, 'almacenista/config_productos.html',
                  {'tipos': tipos, 'tallas': tallas, 'colores': colores})


TABLAS = {
    "centros":   CentroFormacion,
    "programas": Programa,
    "tipos":     TipoProducto,
    "tallas":    Talla,
    "colores":   Color,
}

def listado_tablas(request):
    tabla = request.GET.get("tabla")
    modelo = TABLAS.get(tabla)
    if not modelo:
        return JsonResponse({"error": "Tabla no válida"}, status=400)

    registros = modelo.objects.all()

    if request.GET.get("fmt") == "html":
        html = render_to_string("almacenista/_tbody_fragment.html", {"objetos": registros})
        return HttpResponse(html)

    data = [{"id": obj.pk, "nombre": obj.nombre} for obj in registros]
    return JsonResponse({"items": data})


@require_POST
def eliminar_palabra(request):
    try:
        tabla = request.GET.get('tabla')
        modelo = TABLAS.get(tabla)
        if not modelo:
            return JsonResponse({'error': 'Tabla inválida'}, status=400)

        obj = get_object_or_404(modelo, pk=request.GET.get('id'))
        obj.delete()
        return JsonResponse({'ok': True})          # 200 por defecto
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)



@login_required
def gestion_palabras(request):
    centros = CentroFormacion.objects.all().order_by('nombre')
    return render(request, 'almacenista/gestion_palabras.html', {
        'centros': centros
    })


# Vista para agregar tipos de productos
@require_POST
@login_required
def agregar_tipo(request):
    nombre = request.POST.get('nombre', '').strip().capitalize()
    if not nombre:
        return JsonResponse({'success': False, 'message': 'Ingresa un nombre de tipo.'})

    tipo, created = TipoProducto.objects.get_or_create(nombre=nombre)
    if created:
        return JsonResponse({'success': True, 'message': f"Tipo '{tipo.nombre}' agregado correctamente."})
    else:
        return JsonResponse({'success': False, 'message': f"El tipo '{tipo.nombre}' ya existe."})


# Vista para agregar tallas
@require_POST
@login_required
def agregar_talla(request):
    nombre = request.POST.get('nombre', '').strip().upper()
    if not nombre:
        return JsonResponse({'success': False, 'message': 'Ingresa una talla.'})

    talla, created = Talla.objects.get_or_create(nombre=nombre)
    if created:
        return JsonResponse({'success': True, 'message': f"Talla '{talla.nombre}' agregada correctamente."})
    else:
        return JsonResponse({'success': False, 'message': f"La talla '{talla.nombre}' ya existe."})


# Vista para agregar colores
@require_POST
@login_required
def agregar_color(request):
    nombre = request.POST.get('nombre', '').strip().capitalize()
    if not nombre:
        return JsonResponse({'success': False, 'message': 'Ingresa un color.'})

    color, created = Color.objects.get_or_create(nombre=nombre)
    if created:
        return JsonResponse({'success': True, 'message': f"Color '{color.nombre}' agregado correctamente."})
    else:
        return JsonResponse({'success': False, 'message': f"El color '{color.nombre}' ya existe."})



@csrf_exempt
def editar_producto(request, producto_id):
    """
    Vista para editar un producto existente.
    
    Permite modificar tipo, talla, color, precio, stock e imagen de un producto.
    Retorna una respuesta JSON con el estado de la operación.
    
    Args:
        request: Objeto HttpRequest con los datos del formulario (POST)
        producto_id: ID del producto a editar
        
    Returns:
        JsonResponse: Estado de la operación (ok o error)
    """
    try:
        producto = Producto.objects.get(id_producto=producto_id)
    except Producto.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)

    if request.method == 'POST':
        tipo_nombre = request.POST.get('tipo')   # ahora viene el texto
        talla_nombre = request.POST.get('talla')
        color_nombre = request.POST.get('color')
        stock = request.POST.get('cantidad')
        precio = request.POST.get('precio')
        imagen_file = request.FILES.get('imagen')

        # Actualizar FK usando get_or_create con nombre
        if tipo_nombre:
            tipo_obj, _ = TipoProducto.objects.get_or_create(nombre=tipo_nombre)
            producto.tipo = tipo_obj
        if talla_nombre:
            talla_obj, _ = Talla.objects.get_or_create(nombre=talla_nombre)
            producto.talla = talla_obj
        if color_nombre:
            color_obj, _ = Color.objects.get_or_create(nombre=color_nombre)
            producto.color = color_obj

        # Actualizar stock y precio
        if stock:
            try:
                producto.stock = int(stock)
            except ValueError:
                pass
        if precio:
            try:
                producto.precio = float(precio)
            except ValueError:
                pass

        # Actualizar imagen si se envía
        if imagen_file:
            carpeta = os.path.join(settings.MEDIA_ROOT, 'productos')
            os.makedirs(carpeta, exist_ok=True)
            ruta_completa = os.path.join(carpeta, imagen_file.name)
            with open(ruta_completa, 'wb+') as f:
                for chunk in imagen_file.chunks():
                    f.write(chunk)
            producto.imagen = f'productos/{imagen_file.name}'

        producto.save()
        return JsonResponse({'status': 'ok', 'producto_id': producto.id_producto})

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


# Vista para eliminar productos
from django.http import JsonResponse
from django.db.models import ProtectedError

@require_POST
def eliminar_producto(request, producto_id):
    try:
        producto = get_object_or_404(Producto, id_producto=producto_id)
        producto.delete()
        return JsonResponse({
            'status': 'ok',
            'message': 'Producto eliminado correctamente'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)



def solicitudes_inventario(request):
    """
    Vista para mostrar las solicitudes pendientes de revisión.
    
    Muestra todas las solicitudes que no están canceladas, despachadas,
    rechazadas o entregadas, ordenadas por fecha de solicitud.
    
    Args:
        request: Objeto HttpRequest del usuario autenticado
        
    Returns:
        HttpResponse: Renderiza la página de solicitudes de inventario
    """
    solicitudes = ( 
    Solicitud.objects
    .select_related("id_aprendiz", "id_producto")
    .exclude(estado_solicitud__in=["cancelada", "despachada", "rechazada", "borrador", "entregada"])
    )
    
    # ordenar por fecha de solicitud
    solicitudes = solicitudes.order_by("-fecha_solicitud")
    return render(request, 'almacenista/Solicitudes_inventario.html', {"solicitudes": solicitudes})


@login_required
def rechazar_solicitud(request, solicitud_id):
    """
    Vista para rechazar una solicitud pendiente.
    
    Cambia el estado de la solicitud a "rechazada", devuelve el stock
    al inventario y envía un correo de notificación al aprendiz.
    
    Args:
        request: Objeto HttpRequest del usuario autenticado
        solicitud_id: ID de la solicitud a rechazar
        
    Returns:
        HttpResponseRedirect: Redirige a la página de solicitudes de inventario
    """
    solicitud = get_object_or_404(Solicitud, id_solicitud=solicitud_id)

    if solicitud.estado_solicitud == "pendiente":
        solicitud.estado_solicitud = "rechazada"
        solicitud.save()

    # Contenido texto del correo
    text_content = (
        f"Hola {solicitud.id_aprendiz.get_full_name() or solicitud.id_aprendiz.username},\n\n"
        f"Lo sentimos, tu solicitud con el ID: #{solicitud.id_solicitud} ha sido rechazada.\n\n"
        f"Si deseas hacer un nuevo pedido, créalo desde nuestro sitio web.\n\n"
        f"https://joan2004s.pythonanywhere.com/ \n\n"
        f"Saludos,\nEl equipo de Dotapp"
    )

    # Contenido HTML del correo
    html_content = f"""
    <html>
    <body style="font-family:Arial,Helvetica,sans-serif; background:#f7f7f7; padding:20px;">
        <div style="max-width:600px; margin:auto; background:white; border-radius:10px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,.1);">
            <div style="padding:20px;">
                Hola {solicitud.id_aprendiz.get_full_name() or solicitud.id_aprendiz.username},<br><br>
                Lo sentimos, tu solicitud con el ID: #{solicitud.id_solicitud} ha sido rechazada.<br>
                Si deseas hacer un nuevo pedido, créalo desde nuestro sitio web.<br><br>
                <a href="https://joan2004s.pythonanywhere.com/">Dotapp</a><br><br>
                Saludos,<br>El equipo de Dotapp
            </div>
        </div>
    </body>
    </html>
    """

    msg = EmailMultiAlternatives(
        'Solicitud rechazada - Dotapp',
        text_content,
        'dotappsena@gmail.com',
        [solicitud.id_aprendiz.correo],
    )
    msg.attach_alternative(html_content, "text/html")

    msg.send(fail_silently=False)

    messages.success(request, "Solicitud rechazada exitosamente.")

    return redirect("solicitudes-inventario")


@login_required
def aprobar_solicitud(request, solicitud_id):
    """
    Vista para aprobar una solicitud pendiente.
    
    Cambia el estado de la solicitud de "pendiente" a "aprobada".
    
    Args:
        request: Objeto HttpRequest del usuario autenticado
        solicitud_id: ID de la solicitud a aprobar
        
    Returns:
        HttpResponseRedirect: Redirige a la página de solicitudes de inventario
    """
    solicitud = get_object_or_404(Solicitud, id_solicitud=solicitud_id)

    if solicitud.estado_solicitud == "pendiente":
        solicitud.estado_solicitud = "aprobada"
        solicitud.save()

        try:
            # 🧾 Generar el PDF de la factura
            pdf_bytes = generar_factura_pdf_bytes(solicitud)
        except Exception as e:
            messages.error(request, f"Error al generar la factura: {e}")
            return redirect("solicitudes-inventario")

        # ✉️ Contenido HTML del correo
        html_content = f"""
        <html>
        <body style="font-family:Arial,Helvetica,sans-serif; background:#f7f7f7; padding:20px;">
            <div style="max-width:600px; margin:auto; background:white; border-radius:10px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,.1);">
                <div style="padding:20px;">
                    <p>Hola <strong>{solicitud.id_aprendiz.get_full_name()}</strong>,</p>
                    <p>Felicidades, tu solicitud con el ID: <strong>#{solicitud.id_solicitud}</strong> ha sido aprobada.</p>
                    <p>Adjunto encontrarás tu factura electrónica.</p>
                    <p>Puedes revisar los detalles en nuestra página web:</p>
                    <a href="https://joan2004s.pythonanywhere.com/">Dotapp</a>
                    <p>Saludos,<br>El equipo de Dotapp</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Versión texto plano
        text_content = (
            f"Hola {solicitud.id_aprendiz.get_full_name()},\n\n"
            f"Felicidades, tu solicitud con el ID: #{solicitud.id_solicitud} ha sido aprobada.\n"
            f"Adjunto encontrarás tu factura electrónica.\n\n"
            f"Consulta más detalles en nuestra página web:\n"
            f"https://joan2004s.pythonanywhere.com/\n\n"
            f"Saludos,\nEl equipo de Dotapp"
        )

        # Crear correo
        msg = EmailMultiAlternatives(
            'Solicitud aprobada - Dotapp',
            text_content,
            'dotappsena@gmail.com',
            [solicitud.id_aprendiz.correo],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.attach(f'factura_{solicitud.id_solicitud}.pdf', pdf_bytes, 'application/pdf')

        try:
            # Enviar correo
            msg.send(fail_silently=False)
            messages.success(request, "Solicitud aprobada exitosamente y factura enviada al aprendiz.")
        except Exception as e:
            messages.error(request, f"La solicitud fue aprobada, pero no se pudo enviar el correo: {e}")

    return redirect("solicitudes-inventario")


@login_required
def despachar_solicitud(request, solicitud_id):
    """
    Vista para despachar una solicitud aprobada.
    
    Cambia el estado de la solicitud de "aprobada" a "despachada"
    y envía un correo de notificación al aprendiz.
    
    Args:
        request: Objeto HttpRequest del usuario autenticado
        solicitud_id: ID de la solicitud a despachar
        
    Returns:
        HttpResponseRedirect: Redirige a la página de solicitudes de inventario
    """
    solicitud = get_object_or_404(Solicitud, id_solicitud=solicitud_id)

    if solicitud.estado_solicitud == "aprobada":
        solicitud.estado_solicitud = "despachada"
        solicitud.save()

    # Contenido texto opcional del correo
    text_content = (
        f'Hola {solicitud.id_aprendiz.get_full_name() or solicitud.id_aprendiz.username},\n\n'
        f'Tu solicitud con el ID: #{solicitud.id_solicitud} ya fué despachada.\n'
        f'Puedes pasar a recogerla en tu centro de formación.\n\n'
        f'Si tienes dudas, puedes revisar todos los detalles en nuestra pagina web.\n\n'
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
                Tu solicitud con el ID: #{solicitud.id_solicitud} ha sido despachada.<br>
                Si tienes dudas, puedes revisar todos los detalles en nuestra pagina web.<br><br>
                <a href="https://joan2004s.pythonanywhere.com/">Dotapp</a><br><br>
                Saludos,<br>El equipo de Dotapp
            </div>
        </div>
    </body>
    </html>
    """

    msg = EmailMultiAlternatives(
        'Solicitud despachada - Dotapp',
        text_content,
        'dotappsena@gmail.com',
        [solicitud.id_aprendiz.correo],
    )
    msg.attach_alternative(html_content, "text/html")

    msg.send(fail_silently=False)

    messages.success(request, "Solicitud despachada exitosamente.")

    return redirect("solicitudes-inventario")