import os
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from core.models import Producto, Solicitud
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from django.urls import reverse


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
    return render(request, 'almacenista/administracion_productos.html', {
        'productos': productos,
        'MEDIA_URL': settings.MEDIA_URL
    })


# Vista para agregar productos
@csrf_exempt
def agregar_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')  # cambiar de 'tipo' a 'nombre'
        precio = request.POST.get('precio')  # agregar campo precio
        talla = request.POST.get('talla')
        color = request.POST.get('color')
        stock = request.POST.get('cantidad')
        imagen_file = request.FILES.get('imagen')

        if not all([nombre, precio, talla, color, stock, imagen_file]):
            return JsonResponse({'status': 'error', 'message': 'Faltan datos'}, status=400)

        # Guardar la imagen en media/productos
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
            nombre=nombre,
            precio=precio,  # asegurarse de pasar el precio
            talla=talla,
            color=color,
            stock=stock,
            imagen=imagen_ruta,
            almacenista=request.user
        )

        return JsonResponse({'status': 'ok', 'producto_id': producto.id_producto})

    return JsonResponse({'status': 'error'}, status=400)



# Vista para editar productos
@csrf_exempt
def editar_producto(request, producto_id):
    try:
        producto = Producto.objects.get(id_producto=producto_id)
    except Producto.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')
        talla = request.POST.get('talla')
        color = request.POST.get('color')
        stock = request.POST.get('cantidad')
        imagen_file = request.FILES.get('imagen')

        if nombre: producto.nombre = nombre
        if talla: producto.talla = talla
        if color: producto.color = color
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

    try:
        producto = Producto.objects.get(id_producto=producto_id)
    except Producto.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Producto no encontrado'}, status=404)

    if request.method == 'POST':
        # Actualizar solo los campos que vienen en el request
        producto = Producto.objects.get(id_producto=producto_id)
        
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')
        talla = request.POST.get('talla')
        color = request.POST.get('color')
        stock = request.POST.get('cantidad')
        imagen_file = request.FILES.get('imagen')

        # Actualizar solo si hay valor
        if nombre: producto.nombre = nombre
        if precio: producto.precio = precio
        if talla: producto.talla = talla
        if color: producto.color = color
        if stock: producto.stock = stock

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
    return render(request, 'almacenista/solicitudes_inventario.html', {"solicitudes": solicitudes})


#vista para rechazar solicitudes
@login_required
def rechazar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id_solicitud=solicitud_id)

    if solicitud.estado_solicitud == "pendiente":
        solicitud.estado_solicitud = "rechazada"
        solicitud.save()

    # Correo al usuario
    send_mail(
        'Solicitud rechazada - Dotapp',
        f'Hola {solicitud.id_aprendiz.get_full_name() or solicitud.id_aprendiz.username},\n\n'
        f'Lo sentimos, tu solicitud con el ID: #{solicitud.id_solicitud} ha sido rechazada.\n\n'
        f'Si tienes dudas, responde a este correo.\n\n'
        f'Saludos,\nEl equipo de Dotapp',
        'dotappsena@gmail.com',
        [solicitud.id_aprendiz.correo],
        fail_silently=False,
    )

    return redirect("solicitudes-inventario")


#vista para aprobar solicitudes
@login_required
def aprobar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id_solicitud=solicitud_id)

    if solicitud.estado_solicitud == "pendiente":
        solicitud.estado_solicitud = "aprobada"
        solicitud.save()

    send_mail(
        'Solicitud aprobada - Dotapp',
        f'Hola {solicitud.id_aprendiz.get_full_name() or solicitud.id_aprendiz.username},\n\n'
        f'¡Felicidades! Tu solicitud con el ID: #{solicitud.id_solicitud} ha sido aprobada!\n'
        f'En breve iniciaremos el despacho. Te avisaremos cuando el pedido esté listo.\n\n'
        f'Gracias por usar Dotapp.\n\n'
        f'Saludos,\nEl equipo de Dotapp',
        'dotappsena@gmail.com',
        [solicitud.id_aprendiz.correo],
        fail_silently=False,
    )

    return redirect("solicitudes-inventario")


#vista para despachar solicitudes
@login_required
def despachar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id_solicitud=solicitud_id)

    if solicitud.estado_solicitud == "aprobada":
        solicitud.estado_solicitud = "despachada"
        solicitud.save()

    send_mail(
        'Solicitud despachada - Dotapp',
        f'Hola {solicitud.id_aprendiz.get_full_name() or solicitud.id_aprendiz.username},\n\n'
        f'Tu solicitud con el ID: #{solicitud.id_solicitud} ya fué despachada.\n'
        f'Puedes pasar a recogerla en tu centro de formación.\n\n'
        f'Si tienes dudas, puedes revisar todos los detalles en nuestra pagina web.\n\n'
        f'Muchas gracias por tu paciencia.\n\n'
        f'Saludos,\nEl equipo de Dotapp',
        'dotappsena@gmail.com',
        [solicitud.id_aprendiz.correo],
        fail_silently=False,
    )

    return redirect("solicitudes-inventario")