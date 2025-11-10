"""
Configuración de Django para el proyecto DotApp SENA

Este archivo contiene todas las configuraciones del proyecto Django, incluyendo:
- Configuración de base de datos
- Aplicaciones instaladas
- Middleware
- Configuración de autenticación personalizada
- Configuración de email (SendGrid)
- Configuración de archivos estáticos y media
- Configuración de seguridad y sesiones

Generado con 'django-admin startproject' usando Django 5.2.6.

Para más información sobre este archivo, ver:
https://docs.djangoproject.com/en/5.2/topics/settings/

Para la lista completa de configuraciones y sus valores, ver:
https://docs.djangoproject.com/en/5.2/ref/settings/
"""
import os
from pathlib import Path

# ============================================================================
# CONFIGURACIÓN DE RUTAS BASE
# ============================================================================

# Directorio base del proyecto
# Resuelve la ruta absoluta del directorio que contiene este archivo (settings.py)
# y luego sube un nivel para obtener el directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

# ============================================================================
# CONFIGURACIÓN DE ARCHIVOS MEDIA
# ============================================================================

# URL base para servir archivos media (imágenes, documentos subidos por usuarios)
# Los archivos se acceden mediante: http://dominio/media/ruta_archivo
MEDIA_URL = '/media/'

# Ruta física en el sistema de archivos donde se almacenan los archivos media
# Se crea automáticamente en el directorio raíz del proyecto
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ============================================================================
# CONFIGURACIÓN DE SEGURIDAD
# ============================================================================

# Esta clave se utiliza para firmar cookies, tokens CSRF, sesiones, etc.
# En producción, debe almacenarse como variable de entorno y nunca
# compartirse públicamente. La clave actual es solo para desarrollo.
SECRET_KEY = 'django-insecure-bldz-ub#xxgikikqukz=oi6rool&z0c&a1$rw_ejzavj^bp1ov'

# ADVERTENCIA DE SEGURIDAD: No ejecutar con DEBUG activado en producción!
# DEBUG = True muestra información detallada de errores (útil en desarrollo)
# DEBUG = False oculta información sensible y mejora el rendimiento (producción)
DEBUG = False

# Lista de hosts/dominios permitidos para servir la aplicación
# Django solo responderá a peticiones de estos dominios por seguridad
# Se incluyen localhost para desarrollo y el dominio de producción
ALLOWED_HOSTS = [
    '127.0.0.1',                      # Localhost IPv4
    'localhost',                      # Localhost nombre
    '.pythonanywhere.com',            # Todos los subdominios de PythonAnywhere
    'joan2004s.pythonanywhere.com'   # Dominio específico de producción
]



# ============================================================================
# DEFINICIÓN DE APLICACIONES
# ============================================================================

# Lista de aplicaciones Django instaladas en el proyecto
# Django carga estas aplicaciones en el orden especificado
INSTALLED_APPS = [
    # Aplicaciones integradas de Django (contrib)
    'django.contrib.admin',           # Panel de administración de Django
    'django.contrib.auth',             # Sistema de autenticación y autorización
    'django.contrib.contenttypes',    # Framework de tipos de contenido
    'django.contrib.sessions',        # Manejo de sesiones
    'django.contrib.messages',        # Sistema de mensajes flash
    'django.contrib.staticfiles',     # Manejo de archivos estáticos (CSS, JS, imágenes)

    # Django Rest Framework
    # Framework para construir APIs REST
    'rest_framework',

    # Aplicación central del proyecto
    # Contiene modelos base, usuarios personalizados, middleware, señales
    'core',

    # Aplicaciones por rol de usuario
    # Cada app maneja las funcionalidades específicas de cada rol
    'administrador',                  # Panel y gestión para administradores
    'almacenista',                    # Gestión de inventario y productos
    'aprendiz',                       # Panel y solicitudes para aprendices
    'despachador',                    # Gestión de entregas y despachos
]

# ============================================================================
# MIDDLEWARE
# ============================================================================

# Middleware se ejecuta en el orden especificado para cada petición HTTP
# Procesan las peticiones antes de llegar a las vistas y las respuestas después
MIDDLEWARE = [
    # Middleware de seguridad de Django
    # Agrega headers de seguridad HTTP (HSTS, X-Content-Type-Options, etc.)
    "django.middleware.security.SecurityMiddleware",
    
    # Middleware de sesiones
    # Maneja el almacenamiento de datos de sesión
    "django.contrib.sessions.middleware.SessionMiddleware",
    
    # Middleware común
    # Procesa peticiones comunes (normalización de URLs, etc.)
    "django.middleware.common.CommonMiddleware",
    
    # Middleware CSRF (Cross-Site Request Forgery)
    # Protege contra ataques CSRF validando tokens en formularios POST
    "django.middleware.csrf.CsrfViewMiddleware",
    
    # Middleware de autenticación
    # Asocia usuarios con peticiones basándose en sesiones
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    
    # Middleware de mensajes
    # Permite pasar mensajes entre peticiones (mensajes flash)
    "django.contrib.messages.middleware.MessageMiddleware",
    
    # Middleware de protección contra clickjacking
    # Previene que la página se cargue en un iframe (X-Frame-Options)
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    
    # Middleware personalizado: Guarda el último template renderizado
    # Útil para debugging y seguimiento de navegación
    "core.middleware.SaveLastTemplateMiddleware",
    
    # Middleware personalizado: Manejo amigable de excepciones
    # Convierte errores técnicos en mensajes amigables para el usuario
    "core.middleware.AmigableExceptionMiddleware",
]

# ============================================================================
# CONFIGURACIÓN DE URLs Y TEMPLATES
# ============================================================================

# Módulo Python que contiene las URLs raíz del proyecto
# Django busca este módulo para enrutar las peticiones HTTP
ROOT_URLCONF = 'Dotapp.urls'

# Configuración del motor de plantillas Django
TEMPLATES = [
    {
        # Motor de plantillas de Django (DjangoTemplates)
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        
        # Directorios adicionales donde buscar plantillas
        # Se busca primero en estos directorios, luego en cada app
        'DIRS': [os.path.join(BASE_DIR, "templates")],
        
        # Habilitar búsqueda de plantillas en directorios 'templates' de cada app
        'APP_DIRS': True,
        
        # Opciones adicionales del motor de plantillas
        'OPTIONS': {
            # Procesadores de contexto: Agregan variables automáticamente a todos los templates
            'context_processors': [
                'django.template.context_processors.request',      # Objeto request disponible en templates
                'django.contrib.auth.context_processors.auth',      # Usuario autenticado (user, perms)
                'django.contrib.messages.context_processors.messages',  # Mensajes flash (messages)
            ],
        },
    },
]

# Aplicación WSGI para el servidor de producción
# WSGI (Web Server Gateway Interface) es el estándar para conectar Django con servidores web
WSGI_APPLICATION = 'Dotapp.wsgi.application'


# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# ============================================================================
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Configuración de la base de datos MySQL para producción
# MySQL es más robusto que SQLite para aplicaciones en producción
# con múltiples usuarios concurrentes
DATABASES = {
    'default': {
        # Motor de base de datos: MySQL
        'ENGINE': 'django.db.backends.mysql',
        
        # Nombre de la base de datos
        # En PythonAnywhere, el formato es: usuario$nombre_bd
        'NAME': 'joan2004s$dotapp',
        
        # Usuario de la base de datos
        'USER': 'joan2004s',
        
        # Contraseña de la base de datos
        # ADVERTENCIA: En producción, usar variables de entorno para credenciales
        'PASSWORD': 'Dotappsena01092025',
        
        # Host del servidor de base de datos
        'HOST': 'joan2004s.mysql.pythonanywhere-services.com',
        
        # Puerto de MySQL (puerto estándar)
        'PORT': '3306',
        
        # Opciones adicionales de MySQL
        'OPTIONS': {
            # Establece el modo SQL estricto para mejor integridad de datos
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Configuración alternativa para desarrollo local con SQLite
# SQLite es más simple y no requiere servidor de base de datos separado
# Descomentar para usar en desarrollo local
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
'''



# ============================================================================
# VALIDACIÓN Y HASHING DE CONTRASEÑAS
# ============================================================================
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

# Algoritmos de hashing para contraseñas (en orden de preferencia)
# Django intenta usar el primero, si no está disponible usa el siguiente
PASSWORD_HASHERS = [
   # Argon2: Algoritmo ganador del Password Hashing Competition (más seguro)
   # Requiere la librería argon2-cffi
   'django.contrib.auth.hashers.Argon2PasswordHasher',
   
   # PBKDF2: Algoritmo estándar y ampliamente soportado
   'django.contrib.auth.hashers.PBKDF2PasswordHasher',
   
   # PBKDF2 con SHA1: Versión alternativa (menos seguro que SHA256)
   'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
   
   # BCrypt con SHA256: Algoritmo basado en Blowfish
   'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# Validadores de contraseñas que se ejecutan al crear/actualizar usuarios
# Aseguran que las contraseñas cumplan con requisitos de seguridad
AUTH_PASSWORD_VALIDATORS = [
    {
        # Valida que la contraseña no sea similar a información del usuario
        # (nombre, email, etc.)
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        # Valida que la contraseña tenga una longitud mínima
        # (por defecto: 8 caracteres)
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        # Valida que la contraseña no esté en una lista de contraseñas comunes
        # (evita contraseñas como "password123", "12345678", etc.)
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        # Valida que la contraseña no sea completamente numérica
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ============================================================================
# INTERNACIONALIZACIÓN (i18n) Y LOCALIZACIÓN (l10n)
# ============================================================================
# https://docs.djangoproject.com/en/5.2/topics/i18n/

# Código de idioma por defecto para la aplicación
# 'es-co' = Español de Colombia
LANGUAGE_CODE = 'es-co'

# Zona horaria por defecto
# 'America/Bogota' = Zona horaria de Colombia (UTC-5)
TIME_ZONE = 'America/Bogota'

# Usar zona horaria aware (consciente de timezone)
# Si True, Django almacena fechas/horas en UTC y las convierte según TIME_ZONE
USE_TZ = True

# Habilitar internacionalización
# Permite traducir la aplicación a múltiples idiomas
USE_I18N = True

# Habilitar localización
# Formatea números, fechas y horas según las convenciones locales
USE_L10N = True


# ============================================================================
# ARCHIVOS ESTÁTICOS (CSS, JavaScript, Imágenes)
# ============================================================================
# https://docs.djangoproject.com/en/5.2/howto/static-files/

# URL base para servir archivos estáticos
# Los archivos se acceden mediante: http://dominio/static/ruta_archivo
STATIC_URL = '/static/'

# Directorios adicionales donde buscar archivos estáticos
# Django busca primero en estos directorios, luego en cada app
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# ============================================================================
# CONFIGURACIÓN DE MODELOS
# ============================================================================

# Tipo de campo por defecto para claves primarias automáticas
# BigAutoField crea campos de tipo BIGINT (más grande que AutoField)
# Útil para aplicaciones que pueden tener muchos registros
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================================================
# CONFIGURACIÓN DE AUTENTICACIÓN PERSONALIZADA
# ============================================================================

# Modelo de usuario personalizado
# Reemplaza el modelo User por defecto de Django con uno personalizado
# El modelo 'core.Usuario' permite campos específicos del proyecto
# (nombre, apellido, correo, rol, etc.)
# IMPORTANTE: Esta configuración debe establecerse antes de la primera migración
AUTH_USER_MODEL = 'core.Usuario'

# ============================================================================
# CONFIGURACIÓN DE ENVÍO DE EMAIL (SendGrid)
# ============================================================================

# Backend de email: SendGrid
# SendGrid es un servicio de envío de emails transaccionales
# Requiere la librería: django-sendgrid-backend
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"

# API Key de SendGrid para autenticación
# ADVERTENCIA: En producción, almacenar como variable de entorno
# Nunca compartir públicamente esta clave
SENDGRID_API_KEY = "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"

# Email por defecto que aparece como remitente
# Todos los emails enviados por la aplicación usarán este remitente
DEFAULT_FROM_EMAIL = "dotappsena@gmail.com"



# ============================================================================
# CONFIGURACIÓN DE RECUPERACIÓN DE CONTRASEÑA
# ============================================================================

# Tiempo de validez del enlace de restablecimiento de contraseña (en segundos)
# Después de este tiempo, el enlace expira y el usuario debe solicitar uno nuevo
# 900 segundos = 15 minutos
PASSWORD_RESET_TIMEOUT = 900

# ============================================================================
# CONFIGURACIÓN DE AUTENTICACIÓN Y REDIRECCIONES
# ============================================================================

# URL a la que se redirige cuando un usuario no autenticado intenta acceder
# a una vista protegida con @login_required
LOGIN_URL = '/login/'

# URL a la que se redirige después de cerrar sesión
LOGOUT_REDIRECT_URL = '/login/'

# ============================================================================
# CONFIGURACIÓN DE MENSAJES FLASH DE DJANGO
# ============================================================================

# Importar constantes de mensajes de Django
from django.contrib.messages import constants as messages

# Mapeo de niveles de mensaje a clases CSS
# Permite personalizar cómo se muestran los mensajes en los templates
MESSAGE_TAGS = {
    messages.DEBUG: "debug",      # Mensajes de depuración
    messages.INFO: "info",       # Mensajes informativos
    messages.SUCCESS: "success", # Mensajes de éxito
    messages.WARNING: "warning", # Mensajes de advertencia
    messages.ERROR: "error",     # Mensajes de error
}

# ============================================================================
# CONFIGURACIÓN DE SEGURIDAD CSRF
# ============================================================================

# Vista personalizada que se ejecuta cuando falla la validación CSRF
# Permite mostrar un mensaje amigable en lugar del error por defecto de Django
CSRF_FAILURE_VIEW = "core.views.csrf_error_redirect"

# ============================================================================
# CONFIGURACIÓN DE URL DEL SITIO
# ============================================================================

# URL absoluta del sitio (usado para generar enlaces completos en emails, etc.)
# Cambiar según el dominio de producción
SITE_URL = 'https://joan2004s.pythonanywhere.com'

# ============================================================================
# CONFIGURACIÓN DE SESIONES
# ============================================================================

# Tiempo de expiración de la sesión por inactividad (en segundos)
# Si el usuario no realiza ninguna acción durante este tiempo, la sesión expira
# 1800 segundos = 30 minutos
SESSION_COOKIE_AGE = 1800

# La sesión expira cuando el navegador se cierra
# Si True, la cookie de sesión no persiste después de cerrar el navegador
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Actualiza la cookie de sesión en cada petición
# Si True, el timer de inactividad se reinicia con cada petición del usuario
# Esto significa que la sesión solo expira si el usuario está completamente inactivo
SESSION_SAVE_EVERY_REQUEST = True