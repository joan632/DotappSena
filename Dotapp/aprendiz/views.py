# aprendiz/views.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from core.models import Solicitud, Producto, Borrador

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
from core.models import Solicitud, Producto, Borrador

import base64
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from io import BytesIO
import imgkit
from django.conf import settings


import base64
import imgkit
from django.conf import settings
from django.template.loader import render_to_string
from io import BytesIO

# Ejecutable portable (Windows dev)
IMGKIT_CONFIG = imgkit.config(
    wkhtmltoimage=r'C:\DotappSENA\DOtapp\wkhtmltopdf\wkhtmltoimage.exe'
)

def generar_factura_pdf_bytes(solicitud):
    print('>>> 3) Dentro de generar_factura_pdf_bytes')
    producto_url = solicitud.id_producto.imagen.url
    producto_abs_url = f"{settings.SITE_URL}{producto_url}"
    print('>>> 4) URL absoluta:', producto_abs_url)

    try:
        html_factura = render_to_string('core/factura.html', {
            's': solicitud,
            'total': solicitud.cantidad * solicitud.id_producto.precio,
            'producto_abs_url': producto_abs_url,
        })
        print('>>> 5) HTML renderizado, tamaño:', len(html_factura))

        pdf_bytes = imgkit.from_string(html_factura, False, {
            'format': 'pdf',
            'quiet': ''
        }, config=IMGKIT_CONFIG)
        print('>>> 6) PDF creado, tamaño:', len(pdf_bytes))
        return pdf_bytes

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e






#vista para bienvenida
@login_required
def bienvenido(request):
    return render(request, 'aprendiz/bienvenido.html')

#vista para pagina principal del aprendiz
@login_required
def principal(request):
    return render(request, "aprendiz/principal.html", {
        "usuario": request.user 
    })

#vista para logout del aprendiz (cerrar sesión)
@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

#vista para perfil del aprendiz
@login_required
def perfil(request):
    return render(request, "aprendiz/perfil.html", {
        "usuario": request.user 
    })

#vista para actualizar perfil del aprendiz
@login_required
def actualizar_perfil(request):
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
        
        # Redireccionar a la página de perfil después de guardar
        return redirect('perfil-aprendiz') 
    
    # Si la solicitud no es POST, simplemente renderiza la plantilla de perfil
    return render(request, 'perfil.html', {'usuario': usuario})

#vista para solicitud de uniforme
@login_required
def solicitud_uniforme(request):
    borrador = Borrador.objects.filter(aprendiz=request.user).first()
    productos = Producto.objects.all()
    return render(request, 'aprendiz/creacion_solicitud.html', {
        "productos": productos, 
        "borrador": borrador,
    })

#vista para crear solicitud de uniforme
@login_required
def crear_solicitud(request):
    if request.method == "POST":
        tipo = request.POST.get("tipo")
        talla = request.POST.get("talla")
        color = request.POST.get("color")
        cantidad = int(request.POST.get("cantidad"))
        centro = request.POST.get("centro")
        programa = request.POST.get("programa")
        ficha = int(request.POST.get("ficha"))
        detalles = request.POST.get("detalles")

        # Buscar el producto correspondiente
        try:
            producto = Producto.objects.get(nombre=tipo, talla=talla, color=color)
        except Producto.DoesNotExist:
            return render(request, "aprendiz/creacion_solicitud.html", 
            messages.warning(request, "El producto seleccionado no está disponible."))
        
         # Verificar stock disponible
        if cantidad > producto.stock:
            messages.warning(
                request,
                f"No hay suficiente stock de {producto.nombre}. "
                f"Solo quedan {producto.stock} unidades disponibles."
            )
            return redirect("solicitud-uniforme")
        
        # Crear la solicitud
        solicitud = Solicitud.objects.create(
            id_aprendiz=request.user,
            id_producto=producto,
            talla=talla,
            color=color,
            cantidad=cantidad,
            detalles_adicionales=detalles,
            centro_formacion=centro,
            programa=programa,
            ficha=ficha,
            estado_solicitud="pendiente",
        )

        # ELIMINAR el borrador del usuario 
        Borrador.objects.filter(aprendiz=request.user).delete()
        

        # Generar la imagen de la factura
        if solicitud.estado_solicitud == "pendiente":
            print('>>> 1) Dentro de pendiente, voy a generar PDF')
            pdf_bytes = generar_factura_pdf_bytes(solicitud)
            print('>>> 2) PDF generado, tamaño:', len(pdf_bytes))

            # Data-URI para embeber
            data_uri = f"data:application/pdf;base64,{base64.b64encode(pdf_bytes).decode('utf-8')}"

            # HTML del correo
            html_content = f"""
            <html>
            <body style="font-family:Arial,Helvetica,sans-serif; background:#f7f7f7; padding:20px;">
                <div style="max-width:600px; margin:auto; background:white; border-radius:10px; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,.1);">
                <!-- PDF embebido -->
                <iframe src="{data_uri}" width="100%" height="600" style="border:none;"></iframe>
                <div style="padding:20px;">
                    <p>Hola <strong>{solicitud.id_aprendiz.get_full_name}</strong>,</p>
                    <p>Tu solicitud <strong>#{solicitud.id_solicitud}</strong> ha sido creada con éxito.</p>
                    <p>Saludos,<br>El equipo de Dotapp</p>
                </div>
                </div>
            </body>
            </html>
            """

            # Texto alternativo
            text_content = (
                f"Hola {solicitud.id_aprendiz.get_full_name},\n\n"
                f"Tu solicitud #{solicitud.id_solicitud} ha sido creada con éxito.\n\n"
                f"Saludos,\nEl equipo de Dotapp"
            )

            # Crear correo
            msg = EmailMultiAlternatives(
                'Factura electrónica - Dotapp',
                text_content,
                'dotappsena@gmail.com',
                [solicitud.id_aprendiz.correo],
            )
            msg.attach_alternative(html_content, "text/html")

            # ADJUNTAR el mismo PDF
            msg.attach(f'factura_{solicitud.id_solicitud}.pdf', pdf_bytes, 'application/pdf')

            print('>>> 7) Preparando EmailMultiAlternatives')
            msg.attach_alternative(html_content, "text/html")
            msg.attach(f'factura_{solicitud.id_solicitud}.pdf', pdf_bytes, 'application/pdf')
            print('>>> 8) Adjuntado, voy a enviar')
            msg.send(fail_silently=False)
            print('>>> 9) ¡Correo enviado!')

            # Enviar
            msg.send(fail_silently=False)








        messages.success(request, "Solicitud creada exitosamente")
        return redirect("historial-solicitudes")

    return render(request, "aprendiz/creacion_solicitud.html")



#vista para guardar borrador
@login_required
def guardar_borrador(request):
    if request.method != "POST":
        return redirect("solicitud-uniforme")

    # update_or_create: solo un borrador por usuario
    Borrador.objects.update_or_create(
        aprendiz=request.user,
        defaults={
            "tipo"    : request.POST.get("tipo")   or "",
            "talla"   : request.POST.get("talla")  or "",
            "color"   : request.POST.get("color")  or "",
            "cantidad": int(request.POST.get("cantidad") or 0),
            "centro"  : request.POST.get("centro") or "",
            "programa": request.POST.get("programa") or "",
            "ficha"   : int(request.POST.get("ficha") or 0) or None,
            "detalles": request.POST.get("detalles") or "",
        }
    )
    messages.info(request, "Borrador guardado ✅")
    return redirect("solicitud-uniforme")


#vista para historial de solicitudes                                    
@login_required
def historial_solicitudes(request):
    solicitudes = Solicitud.objects.filter(id_aprendiz=request.user)
    productos = Producto.objects.all()
    return render(request, "aprendiz/historial_solicitudes.html", {
        "solicitudes": solicitudes,
        "productos": productos
    })



#vista para cancelar solicitud
@login_required
def cancelar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(Solicitud, id_solicitud=solicitud_id, id_aprendiz=request.user)

    if solicitud.estado_solicitud == "pendiente":
        solicitud.estado_solicitud = "cancelada"
        solicitud.save()

    send_mail(
        'Solicitud cancelada - Dotapp',
        f'Hola {solicitud.id_aprendiz.get_full_name() or solicitud.id_aprendiz.username},\n\n'
        f'Tu solicitud con el ID: #{solicitud.id_solicitud} ha sido cancelada.\n'
        f'Si deseas hacer un nuevo pedido, créalo desde nuestro sitio web.\n\n'
        f'Saludos,\nEl equipo de Dotapp',
        'dotappsena@gmail.com',
        [solicitud.id_aprendiz.correo],
        fail_silently=False,
    )

    return redirect("historial-solicitudes")
