from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard_despachador, name='dashboard-despachador'),
    path('solicitudes-pendientes/', views.solicitudes_pendientes, name='solicitudes_pendientes'),
    path("entregar/<int:solicitud_id>/", views.entregar_solicitud, name="entregar-solicitud"),
]