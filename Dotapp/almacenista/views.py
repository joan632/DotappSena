import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.models import Producto, Solicitud, TipoProducto, Talla, Color
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse
#import pdfkit
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages
import json

'''
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
    
'''

# Vista para el panel de almacenista
@login_required
def dashboard_almacenista(request):
    if request.user.rol is None or request.user.rol.nombre_rol not in ["administrador", "almacenista"]:
        return redirect(reverse("acceso_denegado"))
    return render(request, "almacenista/dashboard_almacenista.html")


# Vista para la administración de productos
@login_required
def administrar_productos(request):
    productos = Producto.objects.all()
    tipos = TipoProducto.objects.all()
    tallas = Talla.objects.all()
    colores = Color.objects.all()
    return render(request, 'almacenista/administracion_productos.html', {
        'productos': productos,
        'tipos': tipos,
        'tallas': tallas,
        'colores': colores,
        'MEDIA_URL': settings.MEDIA_URL
    })


# Vista para agregar productos
@csrf_exempt
def agregar_producto(request):
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








from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse


@csrf_exempt
def agregar_tipo(request):
    print("✅ Vista agregar_tipo llamada")
    if request.method == 'POST':
        print("🟢 Datos recibidos:", request.POST)
        nombre = request.POST.get('nombre')
        if nombre:
            TipoProducto.objects.create(nombre=nombre)
            print("💾 Guardado:", nombre)
            return HttpResponse("OK")
        else:
            print("⚠️ No se recibió nombre")
    return HttpResponse("Error", status=400)


@csrf_exempt
def agregar_talla(request):
    print("✅ Vista agregar_talla llamada")
    if request.method == 'POST':
        print("🟢 Datos recibidos:", request.POST)
        nombre = request.POST.get('nombre')
        if nombre:
            Talla.objects.create(nombre=nombre)
            print("💾 Guardado:", nombre)
            return HttpResponse("OK")
        else:
            print("⚠️ No se recibió nombre")
    return HttpResponse("Error", status=400)


@csrf_exempt
def agregar_color(request):
    print("✅ Vista agregar_color llamada")
    if request.method == 'POST':
        print("🟢 Datos recibidos:", request.POST)
        nombre = request.POST.get('nombre')
        if nombre:
            Color.objects.create(nombre=nombre)
            print("💾 Guardado:", nombre)
            return HttpResponse("OK")
        else:
            print("⚠️ No se recibió nombre")
    return HttpResponse("Error", status=400)











# Vista para editar productos
@csrf_exempt
def editar_producto(request, producto_id):
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
@csrf_exempt
def eliminar_producto(request, producto_id):
    try:
        producto = Producto.objects.get(id_producto=producto_id)
    except Producto.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)

    producto.delete()
    return JsonResponse({'status': 'ok'})


#vista para solicitudes de inventario
def solicitudes_inventario(request):
    solicitudes = ( 
    Solicitud.objects
    .select_related("id_aprendiz", "id_producto")
    .exclude(estado_solicitud__in=["cancelada", "despachada", "rechazada", "borrador", "entregada"])
    )
    
    # ordenar por fecha de solicitud
    solicitudes = solicitudes.order_by("-fecha_solicitud")
    return render(request, 'almacenista/Solicitudes_inventario.html', {"solicitudes": solicitudes})


#vista para rechazar solicitudes
@login_required
def rechazar_solicitud(request, solicitud_id):
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


#vista para aprobar solicitudes
@login_required
def aprobar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id_solicitud=solicitud_id)

    if solicitud.estado_solicitud == "pendiente":
        solicitud.estado_solicitud = "aprobada"
        solicitud.save()

    return redirect("solicitudes-inventario")
'''
        # Generar el PDF de la factura
        pdf_bytes = generar_factura_pdf_bytes(solicitud)

        # Contenido HTML del correo
        html_content = f"""
        <html>
        <body style="font-family:Arial,Helvetica,sans-serif; background:#f7f7f7; padding:20px;">
            <div style="max-width:600px; margin:auto; background:white; border-radius:10px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,.1);">
                <div style="padding:20px;">
                    <p>Hola <strong>{solicitud.id_aprendiz.get_full_name()}</strong>,</p>
                    <p>Felicidades, Tu solicitud con el ID: <strong>#{solicitud.id_solicitud}</strong> ha sido aprobada.</p>
                    <p>Adjunto encontrarás tu factura electrónica.</p>
                    <p>Si tienes dudas, puedes revisar todos los detalles en nuestra página web:</p>
                    <a href="https://joan2004s.pythonanywhere.com/">Dotapp</a>
                    <p>Saludos,<br>El equipo de Dotapp</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Contenido texto opcional del correo
        text_content = (
            f"Hola {solicitud.id_aprendiz.get_full_name()},\n\n"
            f"Felicidades, Tu solicitud con el ID: #{solicitud.id_solicitud} ha sido aprobada.\n"
            f"Adjunto encontrarás tu factura electrónica.\n\n"
            f"Si tienes dudas, puedes revisar todos los detalles en nuestra pagina web.\n\n"
            f"https://joan2004s.pythonanywhere.com/ \n\n"
            f"Saludos,\nEl equipo de Dotapp"
        )

        # Configurar el correo
        msg = EmailMultiAlternatives(
            'Solicitud aprobada - Dotapp',
            text_content,
            'dotappsena@gmail.com',
            [solicitud.id_aprendiz.correo],
        )

        # Adjuntar el contenido HTML
        msg.attach_alternative(html_content, "text/html")

        # Adjuntar el PDF
        msg.attach(f'factura_solicitud_{solicitud.estado_solicitud}.pdf', pdf_bytes, 'application/pdf')

        # 🚀 Enviar el correo
        msg.send(fail_silently=False)

        messages.success(request, "Solicitud aprobada exitosamente.")

    return redirect("solicitudes-inventario")
'''

#vista para despachar solicitudes
@login_required
def despachar_solicitud(request, solicitud_id):
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