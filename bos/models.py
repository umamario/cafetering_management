from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django_fsm import FSMField, transition


class Universidad(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    ciudad = models.CharField(max_length=30)


class Cafeteria(models.Model):
    id = models.AutoField(primary_key=True)
    facultad = models.CharField(max_length=30)
    universidad = models.ForeignKey(Universidad, on_delete=models.CASCADE)


class Alumno(models.Model):
    id = models.AutoField(primary_key=True)
    fecha_nacimiento = models.DateField()
    universidad = models.ForeignKey(Universidad, on_delete=models.CASCADE)
    cafeteria = models.ForeignKey(Cafeteria, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Empleado(models.Model):
    TIPO_EMPLEADOS = ((1, "Encargado"),
                      (2, "Camarero"),)
    id = models.AutoField(primary_key=True)
    cafeteria = models.ManyToManyField(Cafeteria, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_empleado = models.IntegerField(choices=TIPO_EMPLEADOS,
                                        default=2)


class Feedback(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    comentario = models.CharField(max_length=400, null=True, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)


class Etiqueta(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    imagen = models.ImageField(upload_to='etiquetas/', null=True, blank=True)


class Alergeno(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    imagen = models.ImageField(upload_to='alergenos/', null=True, blank=True)


class Producto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    calorias = models.FloatField(null=True, blank=True)
    grasas_saturadas = models.FloatField(null=True, blank=True)
    precio = models.FloatField()
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    imagen = models.ImageField(null=True, blank=True, upload_to='productos/')
    etiquetas = models.ManyToManyField(Etiqueta, blank=True)
    alergenos = models.ManyToManyField(Alergeno, blank=True)
    precio_oferta = models.FloatField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)


class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    productos = models.ManyToManyField(Producto)


class Resena(models.Model):
    id = models.AutoField(primary_key=True)
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    comentario = models.CharField(max_length=400, null=True, blank=True)
    calificacion = models.IntegerField(null=True, blank=True)
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE)


class Oferta(models.Model):
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    descuento_porcentual = models.IntegerField(null=True, blank=True)
    descuento_numerico = models.FloatField(null=True, blank=True)
    productos = models.ManyToManyField(Producto)
    imagen = models.ImageField(upload_to='oferta/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super(Oferta, self).save(*args, **kwargs)
        for product in self.productos.all():  # It does not work when the offer is created from admin
            if self.descuento_porcentual:
                product.precio_oferta = product.precio * (1 - self.descuento_porcentual / 100)
                product.save()
            elif self.descuento_numerico:
                product.precio_oferta = product.precio - self.descuento_numerico
                product.save()
            else:
                raise ValueError('Offer does not have discount set for PRODUCT ID %d' % producto.id)


class Menu(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    productos = models.ManyToManyField(Producto)



STATES = ('En cola', 'En proceso', 'Preparado', 'Entregado', 'No recogido', 'Cancelado')
STATES = list(zip(STATES, STATES))


class Pedido(models.Model):
    id = models.AutoField(primary_key=True)
    estado = FSMField(default=STATES[0], choices=STATES)
    productos = models.ManyToManyField(Producto)
    menus = models.ManyToManyField(Menu, related_name='menus')
    ofertas = models.ManyToManyField(Menu, related_name='ofertas')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    recogida_estimada = models.DateField()
    fecha_recogida = models.DateField(null=True, blank=True)
    qr = models.ImageField(upload_to='qr/', null=True, blank=True)
    ordenante = models.ManyToManyField(Alumno, related_name='alumnos')
    resenas = models.ManyToManyField(Resena, blank=True)

    @transition(field=estado, source=['En cola'], target='En proceso')
    def start(self):
        """
             This method will contain the action that needs to be taken once the
             state is changed. Such as notifying Users.
        """
        pass

    @transition(field=estado, source='Preparado', target='Entregado')
    def resolve(self):
        """
            This method will contain the action that needs to be taken once the
            state is changed. Such as notifying Users
            Help on https://hashedin.com/blog/a-guide-to-managing-finite-state-machine-using-django-fsm/
        """
        pass
