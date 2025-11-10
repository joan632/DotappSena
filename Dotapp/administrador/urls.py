# administrador/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('panel-admin/', views.panel_admin, name='panel-admin'),
    path('administracion-usuarios/', views.administracion_usuarios, name='administracion-usuarios'),
    path('historial-usuarios/<int:id_usuario>/', views.historial_usuarios, name='historial-usuarios'),
    path("usuarios/editar/<int:id_usuario>/", views.editar_usuario, name="editar-usuario"),
    path("usuarios/eliminar/<int:id_usuario>/", views.eliminar_usuario, name="eliminar-usuario"),
    path("usuarios/estado/<int:id_usuario>/", views.cambiar_estado_usuario, name="cambiar-estado-usuario"),
    path('seguimiento-pedidos/', views.seguimiento_pedidos, name='seguimiento-pedidos'),
    path("export/pdf/", views.exportar_pdf, name="exportar_pdf"),
    path("export/excel/", views.exportar_excel, name="exportar_excel"),


]
