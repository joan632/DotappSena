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

        # Mostrar mensaje de éxito
        messages.success(request, 'Perfil actualizado correctamente.')

        # Redireccionar a la página de perfil después de guardar
        return redirect('perfil-aprendiz')

    # Si la solicitud no es POST, simplemente renderiza la plantilla de perfil
    return render(request, 'perfil.html', {'usuario': usuario})

#vista para solicitud de uniforme
@login_required
def solicitud_uniforme(request):
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


# Vista para filtrar programas por centro (AJAX)

def ajax_programas_por_centro(request):
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
    if request.method == "POST":
        # --- Procesar datos del formulario ---
        tipo_str = request.POST.get("tipo")
        talla_str = request.POST.get("talla")
        color_str = request.POST.get("color")
        cantidad = int(request.POST.get("cantidad") or 0)
        centro_id = request.POST.get("centro")
        programa_id = request.POST.get("programa")
        ficha = int(request.POST.get("ficha") or 0)
        detalles = request.POST.get("detalles") or ""

        # --- Obtener objetos relacionados ---
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

        # --- Crear solicitud correctamente ---
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

        # El método save() del modelo se encarga de copiar los nombres (tipo_nombre, color_nombre, etc.)

        # --- Eliminar borrador ---
        Borrador.objects.filter(aprendiz=request.user).delete()

        messages.success(request, "Solicitud creada exitosamente.")
        return redirect("historial-solicitudes")

    # Si no es POST
    return redirect("solicitud-uniforme")





#vista para guardar borrador
@login_required
def guardar_borrador(request):
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


#vista para historial de solicitudes
@login_required
def historial_solicitudes(request):
    solicitudes = Solicitud.objects.filter(id_aprendiz=request.user)
    return render(request, "aprendiz/historial_solicitudes.html", {
        "solicitudes": solicitudes,
    })



#vista para cancelar solicitud
@login_required
def cancelar_solicitud(request, solicitud_id):
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

