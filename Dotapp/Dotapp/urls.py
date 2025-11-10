from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),

    #  Redirigir la raíz directamente al login (sin conflicto)
    path('', lambda request: redirect('/login/')),

    path('core/', include('core.urls')),
    path('aprendiz/', include('aprendiz.urls')),
    path('administrador/', include('administrador.urls')),
    path('almacenista/', include('almacenista.urls')),
    path('despachador/', include('despachador.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'core.views.error_404_view'
handler500 = 'core.views.error_500_view'
handler403 = 'core.views.error_403_view'
handler400 = 'core.views.error_400_view'
