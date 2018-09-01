from django import template
from bos.models import *

register = template.Library()


@register.filter
def estaCompleto(value):
    if value == 'Entregado' or value == 'No recogido' or value == 'Cancelado':
        return True
    else:
        return False


@register.filter
def mostrarDescuento(value):
    oferta = Oferta.objects.get(pk=int(value))
    if oferta.descuento_porcentual:
        return str(oferta.descuento_porcentual) + "%"
    elif oferta.descuento_numerico:
        return unicode(oferta.descuento_porcentual)
    else:
        return "No definido"


@register.filter
def getProductosID(value):
    menu = Menu.objects.get(pk=int(value))
    out = ""
    for m in menu.productos.all():
        out += " %s -" % m.nombre
    return out[:-1]


@register.filter
def getCantidadProductos(value):
    categoria = Categoria.objects.get(pk=int(value))
    return categoria.productos.all().count()


@register.filter
def classname(obj):
    return obj.__class__.__name__
