"""
URL configuration for Dotapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

    


from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('error/', include('core.urls')),
    path('', redirect_to_login),
    path('', include('core.urls')),
    path('aprendiz/', include('aprendiz.urls')),
    path('administrador/', include('administrador.urls')),
    path('almacenista/', include('almacenista.urls')),
    path('despachador/', include('despachador.urls')),
]
"""



# Dotapp/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('core/', include('core.urls')),

    path('aprendiz/', include('aprendiz.urls')),
    path('administrador/', include('administrador.urls')),
    path('almacenista/', include('almacenista.urls')),
    path('despachador/', include('despachador.urls')),

    # raíz del sitio
    path('', core_views.login_view, name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'core.views.error_404_view'
handler500 = 'core.views.error_500_view'
handler403 = 'core.views.error_403_view'
handler400 = 'core.views.error_400_view'
