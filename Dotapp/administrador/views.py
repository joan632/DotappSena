from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse, HttpResponse
from core.models import Usuario, Rol, Solicitud, Borrador, CentroFormacion, Programa

#vista de panel de administrador
@login_required
def panel_admin(request):
    if request.user.rol is None or request.user.rol.nombre_rol != "administrador":
        return redirect(reverse("acceso_denegado"))
    return render(request, "administrador/panel_admin.html")

#vista de administracion de usuarios
@login_required
def administracion_usuarios(request):
    usuarios = Usuario.objects.filter(is_superuser=False)
    roles = Rol.objects.all()
    return render(request, "administrador/administracion_usuarios.html", {"usuarios": usuarios, "roles": roles})


#vista de historial de usuarios
@login_required
def historial_usuarios(request, id_usuario):
    usuario = get_object_or_404(Usuario, id_usuario=id_usuario)
    solicitudes = usuario.solicitudes.all()
    
    
    # ordenar por fecha de solicitud
    solicitudes = solicitudes.order_by("-fecha_solicitud")
    return render(
        request,
        "administrador/historial-de-usuario.html",
        {
            "usuario": usuario,
            "solicitudes": solicitudes
        }
    )

# vista de editar usuario
@login_required
def editar_usuario(request, id_usuario):
    usuario = get_object_or_404(Usuario, id_usuario=id_usuario)

    # 🚫 Bloquear edición si está inactivo
    if not usuario.is_active:
        return JsonResponse({"success": False, "error": "El usuario está inactivo y no puede ser editado."}, status=403)

    if request.method == "POST":
        nombre = request.POST.get("nombre")
        apellido = request.POST.get("apellido")
        correo = request.POST.get("correo")
        rol_id = request.POST.get("rol")

        if nombre:
            usuario.nombre = nombre
        if apellido:
            usuario.apellido = apellido
        if correo:
            usuario.correo = correo
        if rol_id:
            usuario.rol_id = int(rol_id)

        usuario.save()
        return JsonResponse({"success": True})

    return JsonResponse({
        "id": usuario.id_usuario,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "correo": usuario.correo,
        "rol": usuario.rol.nombre if usuario.rol else None
    })

#vista de eliminar usuario
@login_required
def eliminar_usuario(request, id):
    if request.method == "POST":
        try:
            usuario = Usuario.objects.get(pk=id)

            # 🚫 Bloquear eliminación si está inactivo
            if not usuario.is_active:
                return JsonResponse({"success": False, "error": "No se puede eliminar un usuario inactivo."}, status=403)

            usuario.delete()
            return JsonResponse({"success": True})
        except Usuario.DoesNotExist:
            return JsonResponse({"success": False, "error": "Usuario no encontrado"})
    return JsonResponse({"success": False, "error": "Método no permitido"})


#vista de desactivar usuarios
@csrf_exempt
def cambiar_estado_usuario(request, id):
    if request.method == "POST":
        try:
            usuario = Usuario.objects.get(pk=id)
            data = json.loads(request.body)
            activar = data.get("activar", True)
            usuario.is_active = activar  # o tu campo equivalente
            usuario.save()
            return JsonResponse({"success": True})
        except Usuario.DoesNotExist:
            return JsonResponse({"success": False, "error": "Usuario no encontrado"})
    return JsonResponse({"success": False, "error": "Método no permitido"})


#vista de seguimiento de pedidos
@login_required
def seguimiento_pedidos(request):
    # obtener parámetros GET
    buscar = request.GET.get("buscar", "").strip()
    estado = request.GET.get("estado", "").strip()

    CentroFormacion.objects.all()  # Asegura que la tabla exista

    # queryset base
    solicitudes = Solicitud.objects.select_related("id_aprendiz", "id_producto").all()
    # Agrega esto:
    borradores = Borrador.objects.all().order_by('-creado')

    # ordenar por fecha de solicitud
    solicitudes = solicitudes.order_by("-fecha_solicitud")

    # aplicar filtros en backend
    if buscar:
        solicitudes = solicitudes.filter(
            id_aprendiz__nombre__icontains=buscar
        ) | solicitudes.filter(
            id_producto__nombre__icontains=buscar
        )  # ejemplo, puedes ajustar
    if estado:
        solicitudes = solicitudes.filter(estado_solicitud__iexact=estado)

    return render(request, "administrador/seguimiento-de-pedidos.html", {
        "solicitudes": solicitudes,
        "borradores": borradores,
        "buscar": buscar,
        "estado": estado,
        "centros": CentroFormacion.objects.all()
    })


# 🟢 Agregar Centro de Formación
@csrf_exempt
def agregar_centro(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        if not nombre:
            return JsonResponse({"success": False, "error": "No se envió nombre"}, status=400)
        
        centro, created = CentroFormacion.objects.get_or_create(nombre=nombre)
        return JsonResponse({
            "success": True,
            "created": created,
            "id_centro": centro.id_centro,
            "nombre": centro.nombre
        })
    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)


# 🟡 Agregar Programa
@csrf_exempt
def agregar_programa(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        centro_id = request.POST.get("centro_id")
        if not nombre:
            return JsonResponse({"success": False, "error": "No se envió nombre"}, status=400)
        if not centro_id:
            return JsonResponse({"success": False, "error": "No se envió centro_id"}, status=400)

        try:
            centro = CentroFormacion.objects.get(id_centro=centro_id)
        except CentroFormacion.DoesNotExist:
            return JsonResponse({"success": False, "error": "Centro no existe"}, status=400)

        programa, created = Programa.objects.get_or_create(nombre=nombre, centro=centro)
        return JsonResponse({
            "success": True,
            "created": created,
            "id_programa": programa.id_programa,
            "nombre": programa.nombre,
            "centro": centro.nombre
        })

    return JsonResponse({"success": False, "error": "Método no permitido"}, status=405)














from django.http import HttpResponse
from django.db.models import Q
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, LongTable
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

def exportar_pdf(request):
    buscar = request.GET.get("buscar", "").strip().lower()
    estado = request.GET.get("estado", "").strip().lower()
    usuario = request.GET.get("usuario", "").strip()

    solicitudes = Solicitud.objects.select_related("id_aprendiz", "id_producto").all()

    if buscar:
        solicitudes = solicitudes.filter(
            Q(id_solicitud__icontains=buscar)
            | Q(fecha_solicitud__icontains=buscar)
            | Q(id_aprendiz__nombre__icontains=buscar)
            | Q(id_producto__nombre__icontains=buscar)
            | Q(talla__icontains=buscar)
            | Q(color__icontains=buscar)
            | Q(cantidad__icontains=buscar)
            | Q(centro_formacion__icontains=buscar)
            | Q(programa__icontains=buscar)
            | Q(ficha__icontains=buscar)
            | Q(detalles_adicionales__icontains=buscar)
            | Q(fecha_finalizacion__icontains=buscar)
            | Q(estado_solicitud__icontains=buscar)
        )

    if estado:
        solicitudes = solicitudes.filter(estado_solicitud__iexact=estado)

    if usuario:
        solicitudes = solicitudes.filter(id_aprendiz__nombre__icontains=usuario)

    # 📌 Generar título dinámico
    if estado and usuario:
        titulo = f"Reporte de solicitudes {estado.title()} de {usuario.title()}"
    elif estado and buscar:
        titulo = f"Reporte de solicitudes {estado.title()} ({buscar})"
    elif usuario and buscar:
        titulo = f"Reporte de solicitudes de {usuario.title()} ({buscar})"
    elif estado:
        titulo = f"Reporte de solicitudes {estado.title()}"
    elif usuario:
        titulo = f"Reporte de solicitudes de {usuario.title()}"
    elif buscar:
        titulo = f"Reporte de solicitudes ({buscar})"
    else:
        titulo = "Reporte de todas las solicitudes"

    # 📄 Respuesta PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=solicitudes.pdf"

    doc = SimpleDocTemplate(response, pagesize=landscape(letter))
    styles = getSampleStyleSheet()
    elementos = []

    # 🏷️ Título
    elementos.append(Paragraph(titulo, styles["Title"]))
    elementos.append(Spacer(1, 12))

    # 📊 Datos de la tabla
    data = [[
        "ID", "Fecha", "Usuario", "Producto", "Talla", "Color", "Cantidad",
        "Centro", "Programa", "Ficha", "Detalles Adicionales" ,"Fecha Fin", "Estado"
    ]]

    estilo_celda = ParagraphStyle("Normal", fontSize=7, alignment=1)

    for s in solicitudes:
        data.append([
            str(s.id_solicitud),
             s.fecha_solicitud.strftime("%Y-%m-%d") if s.fecha_solicitud else "",
            str(s.id_aprendiz.get_full_name() if hasattr(s.id_aprendiz, "get_full_name") else s.id_aprendiz),
            str(s.id_producto.nombre if s.id_producto else ""),
            str(s.talla),
            str(s.color),
            str(s.cantidad),
            str(s.centro_formacion),
            str(s.programa),
            str(s.ficha),
            Paragraph(str(s.detalles_adicionales), estilo_celda),
             s.fecha_finalizacion.strftime("%Y-%m-%d") if s.fecha_finalizacion else "",
            str(s.estado_solicitud),
        ])

    # 📐 Ajustar anchos de columnas
    colWidths = [
        35,   
        55,   
        105,  
        50,   
        30,   
        45,   
        40,   
        50,   
        50,   
        50,  
        100,  
        60,   
        60,   
    ]

    table = LongTable(data, repeatRows=1, colWidths=colWidths)

    # 🎨 Estilos de la tabla
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#c3f0ca")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    elementos.append(table)
    doc.build(elementos)

    return response



import openpyxl
from openpyxl.worksheet.table import Table, TableStyleInfo
from django.http import HttpResponse
from django.db.models import Q
from django.utils.timezone import is_aware

def exportar_excel(request):
    buscar = request.GET.get("buscar", "").strip().lower()
    estado = request.GET.get("estado", "").strip().lower()
    usuario = request.GET.get("usuario", "").strip()

    solicitudes = Solicitud.objects.select_related("id_aprendiz", "id_producto").all()

    # 📌 Filtros
    if buscar:
        solicitudes = solicitudes.filter(
            Q(id_solicitud__icontains=buscar)
            | Q(fecha_solicitud__icontains=buscar)
            | Q(id_aprendiz__nombre__icontains=buscar)
            | Q(id_producto__nombre__icontains=buscar)
            | Q(talla__icontains=buscar)
            | Q(color__icontains=buscar)
            | Q(cantidad__icontains=buscar)
            | Q(centro_formacion__icontains=buscar)
            | Q(programa__icontains=buscar)
            | Q(ficha__icontains=buscar)
            | Q(detalles_adicionales__icontains=buscar)
            | Q(fecha_finalizacion__icontains=buscar)
            | Q(estado_solicitud__icontains=buscar)
        )

    if estado:
        solicitudes = solicitudes.filter(estado_solicitud__iexact=estado)

    if usuario:
        solicitudes = solicitudes.filter(id_aprendiz__nombre__icontains=usuario)

    # 📌 Generar título dinámico
    if estado:
        titulo = f"Reporte de solicitudes {estado.title()}"
    elif usuario:
        titulo = f"Reporte de solicitudes de {usuario.title()}"
    elif buscar:
        titulo = f"Reporte de solicitudes (filtro {buscar})"
    else:
        titulo = "Reporte de todas las solicitudes"

    # Crear workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Solicitudes"

    # Encabezados
    headers = [
        "ID Solicitud", "Fecha Solicitud", "Usuario", "Producto", "Talla", "Color", 
        "Cantidad", "Centro de Formación", "Programa", "Ficha",  "Detalles Adicionales",
        "Fecha Finalización", "Estado"
    ]
    ws.append(headers)

    # 📌 Agregar filas
    for solicitud in solicitudes:
        fecha_solicitud = solicitud.fecha_solicitud
        if is_aware(fecha_solicitud):
            fecha_solicitud = fecha_solicitud.replace(tzinfo=None)

        fecha_finalizacion = solicitud.fecha_finalizacion
        if fecha_finalizacion and is_aware(fecha_finalizacion):
            fecha_finalizacion = fecha_finalizacion.replace(tzinfo=None)

        ws.append([
            solicitud.id_solicitud,
            fecha_solicitud,
            solicitud.id_aprendiz.get_full_name() if solicitud.id_aprendiz else "",
            solicitud.id_producto.nombre if solicitud.id_producto else "",
            solicitud.talla,
            solicitud.color,
            solicitud.cantidad,
            solicitud.centro_formacion,
            solicitud.programa,
            solicitud.ficha,
            solicitud.detalles_adicionales or "",
            fecha_finalizacion,
            solicitud.estado_solicitud.title(),
        ])

    # Tabla con estilo
    table = Table(displayName="TablaSolicitudes", ref=f"A1:M{ws.max_row}")
    style = TableStyleInfo(
        name="TableStyleMedium9", showFirstColumn=False,
        showLastColumn=False, showRowStripes=True, showColumnStripes=True
    )
    table.tableStyleInfo = style
    ws.add_table(table)

    # 📌 Nombre dinámico del archivo
    filename = f"{titulo.replace(' ', '_').lower()}.xlsx"

    # Respuesta HTTP
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response









