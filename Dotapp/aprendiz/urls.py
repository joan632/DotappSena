from django.urls import path
from . import views

urlpatterns = [
    path('Bienvenido/', views.bienvenido, name='bienvenido-aprendiz'),
    path("principal/", views.principal, name="principal-aprendiz"),
    path("logout/", views.logout_view, name="logout"),
    path("perfil/", views.perfil, name="perfil-aprendiz"),
    path('perfil/actualizar/', views.actualizar_perfil, name='actualizar_perfil'),
    path("solicitud_uniforme/", views.solicitud_uniforme, name="solicitud-uniforme"),
    path("historial_solicitudes/", views.historial_solicitudes, name="historial-solicitudes"),
    path("crear-solicitud/", views.crear_solicitud, name="crear_solicitud"),
    path("guardar-borrador/", views.guardar_borrador, name="guardar_borrador"),
    path("cancelar/<int:solicitud_id>/", views.cancelar_solicitud, name="cancelar-solicitud"),
    path('ajax/programas_por_centro/', views.ajax_programas_por_centro, name='ajax_programas_por_centro'),
]

