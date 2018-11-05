from django.contrib import admin

# Register your models here.
from .models import *
from django_fsm_log.models import StateLog

admin.site.register(Universidad)
admin.site.register(Cafeteria)
admin.site.register(Alumno)
admin.site.register(Empleado)
admin.site.register(Etiqueta)
admin.site.register(Alergeno)
admin.site.register(Resena)
admin.site.register(Producto)
admin.site.register(Oferta)
admin.site.register(Menu)
admin.site.register(Pedido)
admin.site.register(Categoria)
admin.site.register(ProductoPedido)
admin.site.register(MenuPedido)
admin.site.register(OfertaPedido)
admin.site.register(OfertaProducto)
admin.site.register(MenuProducto)
admin.site.register(StateLog)
