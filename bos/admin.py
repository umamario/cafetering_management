from django.contrib import admin

# Register your models here.
from .models import *

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