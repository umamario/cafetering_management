from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django_fsm import FSMField, transition
from django.core.validators import RegexValidator
from django_fsm_log.decorators import fsm_log_by

ESTADO_CHOICES = (
    (0, 'Inactivo'),
    (1, 'Activo'),
)


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
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="El telefono debe tener el formato: '+999999999'. Maximo 15 digitos.")
    telefono = models.CharField(validators=[phone_regex], max_length=17, blank=True,
                                null=True)
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
    precio_oferta = models.FloatField(null=True, blank=True, default=0.0)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    estado = models.IntegerField(default=0, choices=ESTADO_CHOICES)
    cafeteria = models.ForeignKey(Cafeteria, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "<Producto #%d; %s>" % (self.id, self.nombre)

class Categoria(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    productos = models.ManyToManyField(Producto)
    estado = models.IntegerField(default=0, choices=ESTADO_CHOICES)
    imagen = models.ImageField(upload_to='categoria/', null=True, blank=True)
    cafeteria = models.ForeignKey(Cafeteria, on_delete=models.CASCADE, null=True)


class Resena(models.Model):
    id = models.AutoField(primary_key=True)
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    comentario = models.CharField(max_length=400, null=True, blank=True)
    calificacion = models.IntegerField(null=True, blank=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)


class Oferta(models.Model):
    id = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    descuento_porcentual = models.IntegerField(null=True, blank=True)
    descuento_numerico = models.FloatField(null=True, blank=True)
    productos = models.ManyToManyField(Producto, through='OfertaProducto')
    imagen = models.ImageField(upload_to='oferta/', null=True, blank=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    estado = models.IntegerField(default=0, choices=ESTADO_CHOICES)
    valido_desde = models.DateTimeField(default=timezone.now)
    valido_hasta = models.DateField(null=True, blank=True)
    precio_oferta = models.FloatField(null=True, blank=True)
    cafeteria = models.ForeignKey(Cafeteria, on_delete=models.CASCADE, null=True)

    def setPrecioOferta(self):
        for product in self.ofertaproducto_set.all():
            if self.descuento_porcentual:
                product.precio_oferta = product.producto.precio * (1 - (float(self.descuento_porcentual) / 100))
            elif self.descuento_numerico:
                product.precio_oferta = 0
            else:
                raise ValueError('Offer does not have discount set for PRODUCT ID %d' % producto.id)
            product.save()

    def save(self, *args, **kwargs):
        super(Oferta, self).save(*args, **kwargs)
        from django.db.models import Sum
        if self.descuento_porcentual or self.descuento_numerico:
            self.setPrecioOferta()
            if not self.precio_oferta:
                self.precio_oferta = self.productos.aggregate(Sum('precio_oferta'))['precio_oferta__sum']
                super(Oferta, self).save(*args, **kwargs)


class Menu(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=200, null=True, blank=True)
    productos = models.ManyToManyField(Producto, through='MenuProducto')
    estado = models.IntegerField(default=0, choices=ESTADO_CHOICES)
    imagen = models.ImageField(upload_to='menu/', null=True, blank=True)
    precio = models.FloatField(null=True, blank=True)
    valido_hasta = models.DateField(null=True, blank=True)
    cafeteria = models.ForeignKey(Cafeteria, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return "<Menu: %s>" % self.nombre


STATES_STR = ('En cola', 'En proceso', 'Preparado', 'Entregado', 'No recogido', 'Cancelado')
STATES = list(zip(STATES_STR, STATES_STR))


class Pedido(models.Model):
    id = models.AutoField(primary_key=True)
    estado = FSMField(default=STATES[0], choices=STATES)
    productos = models.ManyToManyField(Producto, through='ProductoPedido')
    menus = models.ManyToManyField(Menu, through='MenuPedido')
    ofertas = models.ManyToManyField(Oferta, through='OfertaPedido')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    recogida_estimada = models.DateTimeField()
    fecha_recogida = models.DateTimeField(null=True, blank=True)
    qr = models.ImageField(upload_to='qr/', null=True, blank=True)
    ordenante = models.ManyToManyField(Alumno, related_name='alumnos')
    resenas = models.ManyToManyField(Resena, blank=True)
    importe = models.FloatField(null=True, blank=True)
    codigo_confirmacion = models.CharField(unique=True, null=True, blank=True, max_length=10)
    observaciones = models.CharField(max_length=60, null=True, blank=True)
    cafeteria = models.ForeignKey(Cafeteria, on_delete=models.CASCADE, null=True)

    def set_estado(self, new_estado, user):
        if new_estado == u"Entregado":
            self.recogido(by=user)
            self.fecha_recogida = timezone.now()
        elif new_estado == u"Cancelado":
            self.cancelar(by=user)
        elif new_estado == u"En cola":
            self.en_cola(by=user)
        elif self.estado == u"En cola" and new_estado == u"En proceso":
            self.preparando(by=user)
        elif self.estado == u"En proceso" and new_estado == u"Preparado":
            self.preparado(by=user)
        elif self.estado == u"Preparado" and new_estado == u"No recogido":
            self.no_recogido(by=user)
        else:
            self.estado = new_estado

    @property
    def hasResena(self):
        return self.resenas.exists()

    @property
    def importe_productos(self):
        productos = self.productopedido_set.all()
        total = 0.0
        for producto in productos:
            total += producto.subtotal
        return total

    @property
    def importe_ofertas(self):
        ofertas = self.ofertapedido_set.all()
        total = 0.0
        for oferta in ofertas:
            total += oferta.subtotal
        return total

    @property
    def importe_menus(self):
        menus = self.menupedido_set.all()
        total = 0.0
        for menu in menus:
            total += menu.subtotal
        return total

    @property
    def generate_confirmation_code(self):
        import string
        import random
        code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        while Pedido.objects.filter(codigo_confirmacion=code):
            code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
        return code

    @property
    def importe_total(self):
        return self.importe_productos + self.importe_ofertas + self.importe_menus

    def __str__(self):
        return "<Pedido %d; %s>" % (self.id, self.get_estado_display())

    def save(self, *args, **kwargs):
        self.importe = self.importe_total
        if not self.codigo_confirmacion:
            self.codigo_confirmacion = self.generate_confirmation_code

        super(Pedido, self).save(*args, **kwargs)

        if not self.qr:
            import qrcode
            from StringIO import StringIO
            from django.core.files.uploadedfile import InMemoryUploadedFile
            img = qrcode.make(self.codigo_confirmacion, box_size=8, border=1)
            buffer = StringIO()
            img.save(buffer, "PNG")
            image_file = InMemoryUploadedFile(buffer, None, 'qr.png', 'image/png', buffer.len, None)
            self.qr.save(u'qr-%d.png' % self.id, image_file)

    @fsm_log_by
    @transition(field=estado, source=['*'], target='En cola')
    def en_cola(self, by=None):
        pass

    @fsm_log_by
    @transition(field=estado, source=['En cola'], target='En proceso')
    def preparando(self, by=None):
        pass

    @fsm_log_by
    @transition(field=estado, source='*', target='Cancelado')
    def cancelar(self, by=None):
        pass

    @fsm_log_by
    @transition(field=estado, source='*', target='Entregado')
    def recogido(self, by=None):
        pass

    @fsm_log_by
    @transition(field=estado, source='*', target='No recogido')
    def no_recogido(self, by=None):
        pass

    @fsm_log_by
    @transition(field=estado, source='*', target='Cancelado')
    def cancelar(self, by=None):
        pass

    @fsm_log_by
    @transition(field=estado, source='*', target='Preparado')
    def preparado(self, by=None):
        pass


class ProductoPedido(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    precio_producto = models.FloatField(null=True, blank=True)

    @property
    def subtotal(self):
        return self.precio_producto * self.quantity


class MenuPedido(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    precio_menu = models.FloatField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.precio_menu * self.quantity

    def __str__(self):
        return "<MenuPedido: %s;#%d>" % (self.menu.nombre, self.pedido.id)


class OfertaPedido(models.Model):
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    precio_oferta = models.FloatField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.precio_oferta * self.quantity


class OfertaProducto(models.Model):
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    precio_oferta = models.FloatField(null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def subtotal(self):
        return self.precio_oferta * self.quantity


class MenuProducto(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
