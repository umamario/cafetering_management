from django.db import models

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


# Create your models here.

class Universidad(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    ciudad = models.CharField(max_length=30)


class Cafeteria(models.Model):
    id = models.AutoField(primary_key=True)
    facultad = models.CharField(max_length=30)
    universidad = models.ForeignKey(Universidad, on_delete=models.CASCADE)


# Hacer que extienda de users
class Alumno(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    apellido = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    fecha_nacimiento = models.DateField()
    universidad = models.ForeignKey(Universidad, on_delete=models.CASCADE)
    cafeteria = models.ForeignKey(Cafeteria, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


# Hacer que extienda de users
class Empleado(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    apellido = models.CharField(max_length=30)
    cafeteria = models.ForeignKey(Cafeteria, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Empleado.objects.create(user=instance)
#
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()


#   Hacer que extienda de users
# class Gerente(models.Model):
#     id = models.AutoField(primary_key=True)
#     nombre = models.CharField(max_length=30)
#     apellido = models.CharField(max_length=30)
#     cafeterias = models.ManyToManyField(Cafeteria)

class Resena(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    comentario = models.CharField(max_length=400, null=True, blank=True)
    calificacion = models.IntegerField(null=True, blank=True)

class Etiqueta(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    imagen = models.ImageField(upload_to='etiquetas/', null=True)


class Alergeno(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    imagen = models.ImageField(upload_to='alergenos/', null=True)


class Producto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    calorias = models.FloatField(null=True, blank=True)
    grasas_saturadas = models.FloatField(null=True, blank=True)
    precio = models.FloatField()
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    imagen = models.ImageField(null=True, blank=True, upload_to='productos/')
    etiquetas = models.ManyToManyField(Etiqueta, null=True, blank=True)
    alergenos = models.ManyToManyField(Alergeno, null=True, blank=True)


class Oferta(models.Model):
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    descuento_porcentual = models.IntegerField(null=True, blank=True)
    descuento_numerico = models.FloatField(null=True, blank=True)
    productos = models.ManyToManyField(Producto)


class Menu(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    productos = models.ManyToManyField(Producto)


class Pedido(models.Model):
    id = models.AutoField(primary_key=True)
    EN_COLA = 'EC'
    EN_PROCESO = 'EP'
    PREPARADO = 'P'
    ENTREGADO = 'E'
    NO_RECOGIDO = 'NR'
    CANCELADO = 'C'
    OPCIONES_ESTADO = (
        (EN_COLA, 'En cola'),
        (EN_PROCESO, 'En proceso'),
        (PREPARADO, 'Preparado'),
        (ENTREGADO, 'Entregado'),
        (NO_RECOGIDO, 'No recogido'),
        (CANCELADO, 'Cancelado'),
    )
    estado = models.CharField(
        max_length=2,
        choices=OPCIONES_ESTADO,
        default=EN_COLA,
    )
    productos = models.ManyToManyField(Producto)
    menus = models.ManyToManyField(Menu, null=True, related_name='menus')
    ofertas = models.ManyToManyField(Menu, related_name='ofertas')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    recogida_estimada = models.DateField()
    fecha_recogida = models.DateField(null=True, blank=True)
    qr = models.ImageField(upload_to='qr/', null=True)
    creador = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    alumnos = models.ManyToManyField(Alumno, related_name='alumnos')
    resenas = models.ManyToManyField(Resena)
