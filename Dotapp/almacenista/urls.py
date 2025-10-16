from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_almacenista, name='dashboard-almacenista'),
    path('administrar-productos/',views.administrar_productos, name='administrar-productos'),
    path('agregar-producto/', views.agregar_producto, name='agregar_producto'),
    path('productos/editar/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    path('solicitudes-inventario/',views.solicitudes_inventario, name='solicitudes-inventario'),
    path("Rechazar/<int:solicitud_id>/", views.rechazar_solicitud, name="rechazar-solicitud"),
    path("Aprobar/<int:solicitud_id>/", views.aprobar_solicitud, name="aprobar-solicitud"),
    path("Despachar/<int:solicitud_id>/", views.despachar_solicitud, name="despachar-solicitud"),
    path("agregar_tipo/", views.agregar_tipo, name="agregar_tipo"),
    path("agregar_talla/", views.agregar_talla, name="agregar_talla"),
    path("agregar_color/", views.agregar_color, name="agregar_color"),
]