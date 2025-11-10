# DotApp SENA

Sistema de gestión de solicitudes de uniformes para el Servicio Nacional de Aprendizaje (SENA) de Colombia. Esta aplicación web permite a los aprendices solicitar uniformes, mientras que administradores, almacenistas y despachadores gestionan el proceso completo de solicitudes, inventario y entregas.

## Descripción

DotApp SENA es una plataforma web desarrollada con Django que facilita la gestión integral del proceso de solicitud y entrega de uniformes en los centros de formación del SENA. El sistema está diseñado con un modelo de roles que permite diferentes niveles de acceso y funcionalidades según el tipo de usuario.

## Características Principales

### Para Aprendices
- Registro y autenticación de usuarios
- Solicitud de uniformes con especificaciones (tipo, talla, color)
- Historial de solicitudes realizadas
- Sistema de borradores para guardar solicitudes incompletas
- Cancelación de solicitudes pendientes
- Perfil de usuario editable

### Para Administradores
- Panel de administración completo
- Gestión de usuarios (editar, eliminar o desactivar)
- Aprobación o rechazo de solicitudes
- Visualización de solicitudes y reportes
- Gestión de centros de formación y programas

### Para Almacenistas
- Gestión de inventario de productos
- Creación,edición y eliminación de productos (tipo, talla, color, precio, stock)
- Control de stock automático
- Visualización de solicitudes pendientes

### Para Despachadores
- Gestión de despachos y entregas
- Actualización de estado de solicitudes
- Seguimiento de entregas

### Funcionalidades Generales
- Sistema de autenticación personalizado con roles
- Recuperación de contraseña por correo electrónico
- Generación de reportes en PDF
- Interfaz responsive con soporte para tema claro/oscuro
- Manejo de archivos multimedia (imágenes de productos)
- API REST con Django REST Framework

## Tecnologías Utilizadas

- **Backend**: Django 5.2.6
- **Base de Datos**: SQLite3 (desarrollo) / MySQL (producción)
- **Frontend**: HTML5, CSS3, JavaScript
- **Autenticación**: Sistema personalizado con Argon2
- **API**: Django REST Framework
- **Generación de PDFs**: WeasyPrint, ReportLab
- **Envío de Emails**: SendGrid
- **Manejo de Excel**: openpyxl

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Virtual environment (recomendado)

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd DotappSENA
```

### 2. Crear y activar un entorno virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la base de datos

El proyecto está configurado para usar SQLite3 por defecto. Para usar MySQL en producción, descomentar y configurar la sección de base de datos en `Dotapp/Dotapp/settings.py`.

### 5. Ejecutar migraciones

```bash
cd Dotapp
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear superusuario

```bash
python manage.py createsuperuser
```

### 7. Recopilar archivos estáticos

```bash
python manage.py collectstatic --noinput
```

### 8. Ejecutar el servidor de desarrollo

```bash
python manage.py runserver
```

La aplicación estará disponible en `http://127.0.0.1:8000/`

## Configuración

### Configuración de Email (SendGrid)

Para habilitar el envío de correos electrónicos (recuperación de contraseña, notificaciones), es necesario configurar la API key de SendGrid en `Dotapp/Dotapp/settings.py`:

```python
SENDGRID_API_KEY = "tu_api_key_aqui"
DEFAULT_FROM_EMAIL = "tu_email@ejemplo.com"
```

### Configuración de Base de Datos (Producción)

Para usar MySQL en producción, editar `Dotapp/Dotapp/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nombre_base_datos',
        'USER': 'usuario',
        'PASSWORD': 'contraseña',
        'HOST': 'host',
        'PORT': '3306',
    }
}
```

### Configuración de Seguridad

**IMPORTANTE**: Antes de desplegar en producción:

1. Cambiar `SECRET_KEY` en `settings.py`
2. Establecer `DEBUG = False`
3. Configurar `ALLOWED_HOSTS` con los dominios permitidos
4. Configurar HTTPS
5. Revisar todas las configuraciones de seguridad

## Estructura del Proyecto

```
DotappSENA/
├── Dotapp/
│   ├── administrador/          # App para administradores
│   ├── almacenista/            # App para almacenistas
│   ├── aprendiz/               # App para aprendices
│   ├── core/                   # App central (usuarios, modelos base)
│   ├── despachador/            # App para despachadores
│   ├── Dotapp/                 # Configuración del proyecto
│   │   ├── settings.py         # Configuración principal
│   │   ├── urls.py             # URLs principales
│   │   ├── wsgi.py             # WSGI config
│   │   └── asgi.py             # ASGI config
│   ├── media/                  # Archivos multimedia subidos
│   ├── static/                 # Archivos estáticos (CSS, JS, imágenes)
│   ├── templates/              # Plantillas base
│   ├── db.sqlite3              # Base de datos SQLite
│   └── manage.py               # Script de gestión de Django
├── requirements.txt            # Dependencias del proyecto
└── README.md                   # Este archivo
```

## Roles y Permisos

El sistema maneja cuatro roles principales:

1. **Aprendiz**: Puede crear y gestionar sus propias solicitudes
2. **Administrador**: Acceso completo al sistema, gestión de usuarios y aprobación de solicitudes
3. **Almacenista**: Gestión de inventario y productos
4. **Despachador**: Gestión de despachos y entregas

## Autenticación

- El sistema utiliza un modelo de usuario personalizado (`core.Usuario`)
- Autenticación basada en correo electrónico
- Contraseñas hasheadas con Argon2
- Recuperación de contraseña por email (válida por 15 minutos)
- Sesiones con expiración automática (30 minutos de inactividad)

## Modelos Principales

- **Usuario**: Usuarios del sistema con roles
- **Producto**: Uniformes con tipo, talla, color, precio y stock
- **Solicitud**: Solicitudes de uniformes con estados (pendiente, aprobada, rechazada, entregada, etc.)
- **CentroFormacion**: Centros de formación del SENA
- **Programa**: Programas de formación asociados a centros
- **Borrador**: Borradores de solicitudes guardadas

## URLs Principales

- `/login/` - Inicio de sesión
- `/registro/` - Registro de nuevos aprendices
- `/aprendiz/` - Panel del aprendiz
- `/administrador/` - Panel del administrador
- `/almacenista/` - Panel del almacenista
- `/despachador/` - Panel del despachador


## Comandos Útiles

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor de desarrollo
python manage.py runserver

# Acceder al shell de Django
python manage.py shell
```

## Solución de Problemas

### Error al instalar dependencias
Asegúrate de tener Python 3.8 o superior y pip actualizado:
```bash
python --version
pip install --upgrade pip
```

### Error de migraciones
Si hay problemas con las migraciones:
```bash
python manage.py makemigrations --merge
python manage.py migrate
```

## Licencia

Este proyecto fue desarrollado para el SENA (Servicio Nacional de Aprendizaje de Colombia).

## Desarrollo

### Versión Actual
- **Versión**: 1.0.0
- **Django**: 5.2.6
- **Python**: 3.8+



**Nota**: Este proyecto está en desarrollo activo. Algunas funcionalidades pueden estar en proceso de implementación o mejora.

