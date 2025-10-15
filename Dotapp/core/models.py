from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

#clase Rol
class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.nombre_rol
    

#clase UsuarioManager
class UsuarioManager(BaseUserManager):
    def create_user(self, nombre, apellido, correo, password=None):
        from core.models import Rol
        aprendiz_rol, _ = Rol.objects.get_or_create(nombre_rol='aprendiz')
        if not correo:
            raise ValueError("El usuario debe tener correo electrónico")
        correo = self.normalize_email(correo)
        usuario = self.model(nombre=nombre, apellido=apellido, correo=correo, rol=aprendiz_rol)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, nombre, apellido, correo, password):
        from core.models import Rol
        if self.model.objects.filter(is_superuser=True).exists():
            raise ValueError("Ya existe un superusuario. Solo puede haber uno.")
        admin_rol, _ = Rol.objects.get_or_create(nombre_rol='administrador')
        usuario = self.create_user(nombre, apellido, correo, password)
        usuario.rol = admin_rol
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.save(using=self._db)
        return usuario


#clase Usuario
class Usuario(AbstractBaseUser, PermissionsMixin):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    correo = models.EmailField(unique=True, max_length=255)

    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # ...
    objects = UsuarioManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    def save(self, *args, **kwargs):
        # Asignar rol aprendiz por defecto si no tiene
        if not self.rol:
            aprendiz_rol, _ = Rol.objects.get_or_create(nombre_rol="aprendiz")
            self.rol = aprendiz_rol
        super().save(*args, **kwargs)

    def __str__(self):
        rol_nombre = self.rol.nombre_rol if self.rol else "Sin rol"
        return f"{self.nombre} {self.apellido} ({rol_nombre})"
    
    def get_full_name(self):
        return f"{self.nombre} {self.apellido}"

    def get_short_name(self):
        return self.nombre




# Tabla de tipos de producto
class TipoProducto(models.Model):
    id_tipo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

# Tabla de tallas
class Talla(models.Model):
    id_talla = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.nombre

# Tabla de colores
class Color(models.Model):
    id_color = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.nombre

# Tabla de productos
class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    tipo = models.ForeignKey(
        TipoProducto,
        on_delete=models.CASCADE,
        related_name='productos'
    )
    talla = models.ForeignKey(
        Talla,
        on_delete=models.CASCADE,
        related_name='productos'
    )
    color = models.ForeignKey(
        Color,
        on_delete=models.CASCADE,
        related_name='productos'
    )
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)

    almacenista = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos_creados",
        limit_choices_to={'rol__nombre_rol': 'almacenista'}
    )

    administrador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="productos_administrados",
        limit_choices_to={'rol__nombre_rol': 'administrador'}
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tipo.nombre} - {self.talla.nombre} - {self.color.nombre}"

    @property
    def imagen_url(self):
        if self.imagen:
            return self.imagen.url
        return None


#clase Solicitud
from django.utils.timezone import now

class Solicitud(models.Model):
    id_solicitud = models.AutoField(primary_key=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)

    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    detalles_adicionales = models.TextField(blank=True, null=True)
    talla = models.CharField(max_length=255, blank=False, null=False)  
    color = models.CharField(max_length=255, blank=False, null=False)  

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
        ('despachada', 'Despachada')
    ]
    
    estado_solicitud = models.CharField(max_length=255, choices=ESTADOS, default='pendiente')

    centro_formacion = models.CharField(max_length=255, blank=False, null=False)
    programa = models.CharField(max_length=255, blank=False, null=False)
    ficha = models.PositiveIntegerField(default=0, blank=False, null=False)

    id_aprendiz = models.ForeignKey(
        "Usuario",
        on_delete=models.CASCADE,
        related_name="solicitudes"
    )

    id_producto = models.ForeignKey(
        "Producto",
        on_delete=models.CASCADE,
        related_name="solicitudes"
    )

    def __str__(self):
        return f"Solicitud {self.id_solicitud} - {self.estado_solicitud}"

    def save(self, *args, **kwargs):
        # Si cambia de estado y aún no tiene fecha de finalización, asignarla
        if self.estado_solicitud in ("despachada", "entregada"):
            self.fecha_finalizacion = now()
        elif self.estado_solicitud in ("aprobada", "rechazada", "cancelada") and not self.fecha_finalizacion:
            self.fecha_finalizacion = now()

        super().save(*args, **kwargs)

        # Si cambia de estado a "rechazada", sumar stock
        if self.estado_solicitud == "rechazada":
            producto = self.id_producto
            producto.stock += self.cantidad
            producto.save()

        # Si cambia de estado a "cancelada", sumar stock
        if self.estado_solicitud == "cancelada":
            producto = self.id_producto
            producto.stock += self.cantidad
            producto.save()

        # Si cambia de estado a "pendiente", restar stock
        if self.estado_solicitud == "pendiente":
            producto = self.id_producto
            producto.stock -= self.cantidad
            producto.save()


#clase Borrador
class Borrador(models.Model):
    """Copia ligera de Solicitud sin restricciones de FK ni stock."""
    id_borrador = models.AutoField(primary_key=True)
    aprendiz = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tipo     = models.CharField(max_length=255, blank=True)
    talla    = models.CharField(max_length=255,  blank=True)
    color    = models.CharField(max_length=255, blank=True)
    cantidad = models.PositiveIntegerField(default=0)
    centro   = models.CharField(max_length=255, blank=True)
    programa = models.CharField(max_length=255, blank=True)
    ficha    = models.PositiveIntegerField(null=True, blank=True)
    detalles = models.TextField(blank=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Borrador {self.id} – {self.aprendiz}"