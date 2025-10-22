from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro_aprendiz, name='registro-aprendiz'),
    path('login/', views.login_view, name='login'),
    path('manual/', views.manual, name='manual'),
    path('dashboard/', views.dashboard_admin, name='dashboard_admin'),
    #recuperacion de contraseña
    path("reset/", views.password_reset_request, name="password_reset_request"),
    path("reset/<uidb64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),
    path("acceso_denegado/", views.acceso_denegado, name="acceso_denegado"),
]
