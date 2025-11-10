"""
Modelos principales del sistema DotApp SENA.

Este módulo contiene todos los modelos de datos utilizados en la aplicación,
incluyendo usuarios personalizados, productos, solicitudes y entidades relacionadas.
"""

from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class Rol(models.Model):
    """
    Modelo que representa los roles de usuario en el sistema.
    
    Los roles definen los diferentes tipos de usuarios y sus permisos:
    - aprendiz: Usuario que puede realizar solicitudes
    - administrador: Usuario con acceso completo al sistema
    - almacenista: Usuario que gestiona el inventario
    - despachador: Usuario que gestiona las entregas
    
    Attributes:
        id_rol: Identificador único del rol (clave primaria)
        nombre_rol: Nombre del rol (único en el sistema)
    """
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=255, unique=True)

    def __str__(self):
        """
        Retorna la representación en string del rol.
        
        Returns:
            str: Nombre del rol
        """
        return self.nombre_rol


class UsuarioManager(BaseUserManager):
    """
    Manager personalizado para el modelo Usuario.
    
    Extiende BaseUserManager para proporcionar métodos de creación
    de usuarios y superusuarios con el modelo personalizado.
    """
    
    def create_user(self, nombre, apellido, correo, password=None):
        """
        Crea y retorna un usuario normal con rol de aprendiz por defecto.
        
        Args:
            nombre: Nombre del usuario
            apellido: Apellido del usuario
            correo: Correo electrónico del usuario (debe ser único)
            password: Contraseña del usuario (opcional)
            
        Returns:
            Usuario: Instancia del usuario creado
            
        Raises:
            ValueError: Si el correo no es proporcionado
        """
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
        """
        Crea y retorna un superusuario con rol de administrador.
        
        Solo puede existir un superusuario en el sistema. Si ya existe uno,
        se lanza una excepción.
        
        Args:
            nombre: Nombre del superusuario
            apellido: Apellido del superusuario
            correo: Correo electrónico del superusuario
            password: Contraseña del superusuario
            
        Returns:
            Usuario: Instancia del superusuario creado
            
        Raises:
            ValueError: Si ya existe un superusuario en el sistema
        """
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


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuario personalizado que extiende AbstractBaseUser.
    
    Este modelo reemplaza el modelo User por defecto de Django y utiliza
    el correo electrónico como campo de autenticación en lugar del username.
    
    Attributes:
        id_usuario: Identificador único del usuario (clave primaria)
        nombre: Nombre del usuario
        apellido: Apellido del usuario
        correo: Correo electrónico del usuario (único, usado para autenticación)
        rol: Rol asignado al usuario (ForeignKey a Rol)
        is_active: Indica si el usuario está activo
        is_staff: Indica si el usuario tiene acceso al panel de administración
    """
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    correo = models.EmailField(unique=True, max_length=255)

    rol = models.ForeignKey(Rol, on_delete=models.PROTECT, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'correo'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    def save(self, *args, **kwargs):
        """
        Guarda el usuario en la base de datos.
        
        Si el usuario no tiene un rol asignado, se le asigna automáticamente
        el rol de aprendiz por defecto.
        """
        if not self.rol:
            aprendiz_rol, _ = Rol.objects.get_or_create(nombre_rol="aprendiz")
            self.rol = aprendiz_rol
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Retorna la representación en string del usuario.
        
        Returns:
            str: Nombre completo y rol del usuario
        """
        rol_nombre = self.rol.nombre_rol if self.rol else "Sin rol"
        return f"{self.nombre} {self.apellido} ({rol_nombre})"
    
    def get_full_name(self):
        """
        Retorna el nombre completo del usuario.
        
        Returns:
            str: Nombre y apellido concatenados
        """
        return f"{self.nombre} {self.apellido}"

    def get_short_name(self):
        """
        Retorna el nombre corto del usuario (solo el nombre).
        
        Returns:
            str: Nombre del usuario
        """
        return self.nombre




class TipoProducto(models.Model):
    """
    Modelo que representa los tipos de productos disponibles.
    
    Ejemplos: camiseta, pantalón, chaqueta, etc.
    
    Attributes:
        id_tipo: Identificador único del tipo (clave primaria)
        nombre: Nombre del tipo de producto (único)
    """
    id_tipo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        """
        Retorna la representación en string del tipo de producto.
        
        Returns:
            str: Nombre del tipo de producto
        """
        return self.nombre


class Talla(models.Model):
    """
    Modelo que representa las tallas disponibles para los productos.
    
    Ejemplos: S, M, L, XL, etc.
    
    Attributes:
        id_talla: Identificador único de la talla (clave primaria)
        nombre: Nombre de la talla (único)
    """
    id_talla = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)

    def __str__(self):
        """
        Retorna la representación en string de la talla.
        
        Returns:
            str: Nombre de la talla
        """
        return self.nombre


class Color(models.Model):
    """
    Modelo que representa los colores disponibles para los productos.
    
    Ejemplos: Rojo, Azul, Negro, Blanco, etc.
    
    Attributes:
        id_color: Identificador único del color (clave primaria)
        nombre: Nombre del color (único)
    """
    id_color = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30, unique=True)

    def __str__(self):
        """
        Retorna la representación en string del color.
        
        Returns:
            str: Nombre del color
        """
        return self.nombre


class Producto(models.Model):
    """
    Modelo que representa un producto (uniforme) en el inventario.
    
    Un producto se define por su combinación única de tipo, talla y color.
    Cada producto tiene un precio, stock disponible y puede tener una imagen.
    
    Attributes:
        id_producto: Identificador único del producto (clave primaria)
        tipo: Tipo de producto (ForeignKey a TipoProducto)
        talla: Talla del producto (ForeignKey a Talla)
        color: Color del producto (ForeignKey a Color)
        precio: Precio del producto (DecimalField)
        stock: Cantidad disponible en inventario (PositiveIntegerField)
        imagen: Imagen del producto (ImageField, opcional)
        almacenista: Usuario almacenista que creó el producto (ForeignKey)
        administrador: Usuario administrador asociado (ForeignKey, opcional)
        created_at: Fecha y hora de creación (DateTimeField)
        updated_at: Fecha y hora de última actualización (DateTimeField)
    """
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
        """
        Retorna la representación en string del producto.
        
        Returns:
            str: Descripción del producto (tipo - talla - color)
        """
        return f"{self.tipo.nombre} - {self.talla.nombre} - {self.color.nombre}"

    @property
    def imagen_url(self):
        """
        Retorna la URL de la imagen del producto si existe.
        
        Returns:
            str: URL de la imagen o None si no tiene imagen
        """
        if self.imagen:
            return self.imagen.url
        return None



class CentroFormacion(models.Model):
    """
    Modelo que representa un centro de formación del SENA.
    
    Cada centro de formación puede tener múltiples programas asociados.
    
    Attributes:
        id_centro: Identificador único del centro (clave primaria)
        nombre: Nombre del centro de formación (único)
    """
    id_centro = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)

    def __str__(self):
        """
        Retorna la representación en string del centro.
        
        Returns:
            str: Nombre del centro de formación
        """
        return self.nombre


class Programa(models.Model):
    """
    Modelo que representa un programa de formación del SENA.
    
    Cada programa pertenece a un centro de formación específico.
    
    Attributes:
        id_programa: Identificador único del programa (clave primaria)
        nombre: Nombre del programa (único)
        centro: Centro de formación al que pertenece (ForeignKey)
    """
    id_programa = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, unique=True)
    centro = models.ForeignKey(
        CentroFormacion,
        on_delete=models.CASCADE,
        related_name="programas"
    )

    def __str__(self):
        """
        Retorna la representación en string del programa.
        
        Returns:
            str: Nombre del programa y su centro
        """
        return f"{self.nombre} ({self.centro.nombre})"

from django.utils.timezone import now


class Solicitud(models.Model):
    """
    Modelo que representa una solicitud de uniforme realizada por un aprendiz.
    
    Una solicitud pasa por diferentes estados durante su ciclo de vida:
    - pendiente: Recién creada, esperando aprobación
    - aprobada: Aprobada por el almacenista
    - rechazada: Rechazada por el almacenista
    - despachada: Despachada y lista para entrega
    - entregada: Entregada al aprendiz
    - cancelada: Cancelada por el aprendiz
    
    El modelo utiliza campos híbridos (ForeignKey + CharField) para mantener
    la integridad referencial mientras permite conservar los nombres incluso
    si se eliminan los objetos relacionados.
    
    Attributes:
        id_solicitud: Identificador único de la solicitud (clave primaria)
        fecha_solicitud: Fecha y hora en que se creó la solicitud
        fecha_finalizacion: Fecha y hora en que se finalizó la solicitud
        cantidad: Cantidad de productos solicitados (mínimo 1)
        detalles_adicionales: Información adicional sobre la solicitud (opcional)
        tipo: Tipo de producto (ForeignKey, puede ser NULL)
        tipo_nombre: Nombre del tipo (almacenado como texto)
        talla: Talla del producto (ForeignKey, puede ser NULL)
        talla_nombre: Nombre de la talla (almacenado como texto)
        color: Color del producto (ForeignKey, puede ser NULL)
        color_nombre: Nombre del color (almacenado como texto)
        centro_formacion: Centro de formación (ForeignKey, puede ser NULL)
        centro_nombre: Nombre del centro (almacenado como texto)
        programa: Programa de formación (ForeignKey, puede ser NULL)
        programa_nombre: Nombre del programa (almacenado como texto)
        ficha: Número de ficha del aprendiz
        id_aprendiz: Aprendiz que realizó la solicitud (ForeignKey)
        id_producto: Producto solicitado (ForeignKey, protegido)
        estado_solicitud: Estado actual de la solicitud (CharField con choices)
    """
    id_solicitud = models.AutoField(primary_key=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)

    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    detalles_adicionales = models.TextField(blank=True, null=True)

    # Campos híbridos: ForeignKey + CharField para mantener nombres incluso si se eliminan objetos
    tipo = models.ForeignKey("TipoProducto", on_delete=models.SET_NULL, null=True)
    tipo_nombre = models.CharField(max_length=255, null=True, blank=True)

    talla = models.ForeignKey("Talla", on_delete=models.SET_NULL, null=True)
    talla_nombre = models.CharField(max_length=255, null=True, blank=True)

    color = models.ForeignKey("Color", on_delete=models.SET_NULL, null=True)
    color_nombre = models.CharField(max_length=255, null=True, blank=True)

    centro_formacion = models.ForeignKey("CentroFormacion", on_delete=models.SET_NULL, null=True)
    centro_nombre = models.CharField(max_length=255, null=True, blank=True)

    programa = models.ForeignKey("Programa", on_delete=models.SET_NULL, null=True)
    programa_nombre = models.CharField(max_length=255, null=True, blank=True)

    ficha = models.PositiveIntegerField(default=0)
    id_aprendiz = models.ForeignKey("Usuario", on_delete=models.CASCADE, related_name="solicitudes")
    id_producto = models.ForeignKey("Producto", on_delete=models.PROTECT, related_name="solicitudes")

    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
        ('despachada', 'Despachada'),
    ]

    estado_solicitud = models.CharField(max_length=255, choices=ESTADOS, default='pendiente')

    def save(self, *args, **kwargs):
        """
        Guarda la solicitud en la base de datos con lógica personalizada.
        
        Este método:
        1. Copia los nombres de los objetos relacionados a los campos de texto
        2. Asigna la fecha de finalización según el estado
        3. Actualiza el stock del producto según el estado de la solicitud:
           - pendiente: Resta stock del producto
           - rechazada/cancelada: Suma stock al producto
        """
        # Copiar los nombres actuales al guardar (solo si existen)
        if self.tipo:
            self.tipo_nombre = self.tipo.nombre
        if self.talla:
            self.talla_nombre = self.talla.nombre
        if self.color:
            self.color_nombre = self.color.nombre
        if self.centro_formacion:
            self.centro_nombre = self.centro_formacion.nombre
        if self.programa:
            self.programa_nombre = self.programa.nombre

        # Asignar fecha de finalización según el estado
        if self.estado_solicitud in ("despachada", "entregada"):
            self.fecha_finalizacion = now()
        elif self.estado_solicitud in ("aprobada", "rechazada", "cancelada") and not self.fecha_finalizacion:
            self.fecha_finalizacion = now()

        super().save(*args, **kwargs)

        # Actualizar stock según el estado
        # Si se rechaza o cancela, devolver el stock al inventario
        if self.estado_solicitud == "rechazada":
            producto = self.id_producto
            producto.stock += self.cantidad
            producto.save()

        if self.estado_solicitud == "cancelada":
            producto = self.id_producto
            producto.stock += self.cantidad
            producto.save()

        # Si se crea como pendiente, reservar stock
        if self.estado_solicitud == "pendiente":
            producto = self.id_producto
            producto.stock -= self.cantidad
            producto.save()




'''
class Solicitud(models.Model):
    id_solicitud = models.AutoField(primary_key=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_finalizacion = models.DateTimeField(null=True, blank=True)

    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    detalles_adicionales = models.TextField(blank=True, null=True)
    tipo = models.CharField(max_length=255)
    talla = models.CharField(max_length=255)
    color = models.CharField(max_length=255)


    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('aprobada', 'Aprobada'),
        ('rechazada', 'Rechazada'),
        ('entregada', 'Entregada'),
        ('cancelada', 'Cancelada'),
        ('despachada', 'Despachada')
    ]
    
    estado_solicitud = models.CharField(max_length=255, choices=ESTADOS, default='pendiente')

    centro_formacion = models.CharField(max_length=255)
    programa = models.CharField(max_length=255)

    ficha = models.PositiveIntegerField(default=0, blank=False, null=False)

    id_aprendiz = models.ForeignKey(
        "Usuario",
        on_delete=models.CASCADE,
        related_name="solicitudes"
    )

    id_producto = models.ForeignKey(
        "Producto",
        on_delete=models.PROTECT,
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
'''



class Borrador(models.Model):
    """
    Modelo que representa un borrador de solicitud guardado por un aprendiz.
    
    Permite a los aprendices guardar solicitudes incompletas para completarlas
    más tarde sin perder la información ingresada.
    
    Attributes:
        id_borrador: Identificador único del borrador (clave primaria)
        aprendiz: Aprendiz propietario del borrador (ForeignKey)
        tipo: Tipo de producto (almacenado como texto)
        talla: Talla del producto (almacenado como texto)
        color: Color del producto (almacenado como texto)
        cantidad: Cantidad de productos
        centro: Centro de formación (ForeignKey, opcional)
        programa: Programa de formación (ForeignKey, opcional)
        ficha: Número de ficha del aprendiz (opcional)
        detalles: Detalles adicionales de la solicitud
        creado: Fecha y hora de creación del borrador
        actualizado: Fecha y hora de última actualización
    """
    id_borrador = models.AutoField(primary_key=True)
    aprendiz = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=255, blank=True)
    talla = models.CharField(max_length=255, blank=True)
    color = models.CharField(max_length=255, blank=True)
    cantidad = models.PositiveIntegerField(default=0)
    centro = models.ForeignKey(CentroFormacion, on_delete=models.SET_NULL, null=True, blank=True)
    programa = models.ForeignKey(Programa, on_delete=models.SET_NULL, null=True, blank=True)
    ficha = models.PositiveIntegerField(null=True, blank=True)
    detalles = models.TextField(blank=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        """
        Retorna la representación en string del borrador.
        
        Returns:
            str: Identificador del borrador
        """
        return f"Borrador {self.id_borrador}"



