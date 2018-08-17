import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from bos.models import *
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django_fsm_log.models import StateLog


def logout_view(request):
    logout(request)
    return redirect(login_view)


# @login_required
def index(request):
    return redirect(pedidos_view)


def pedidos_view(request):
    pedidos = Pedido.objects.all()
    return render(request, 'pedidos.html', {'pedidos': pedidos})


def pedido_view(request, pedido_pk):
    pedido = get_object_or_404(Pedido, pk=pedido_pk)
    alumnos = pedido.ordenante.all()
    ofertas = pedido.ofertapedido_set.all()
    menus = pedido.menupedido_set.all()
    productos = pedido.productopedido_set.all()
    statelogs = StateLog.objects.for_(pedido)
    return render(request, 'pedido.html', {'pedido': pedido, 'alumnos': alumnos, 'ofertas': ofertas,
                                           'menus': menus, 'productos': productos, 'statelogs': statelogs})


def categoria_view(request, categoria_pk):
    pass


def oferta_view(request, oferta_pk):
    pass


def menu_view(request, menu_pk):
    pass


def nueva_oferta_view(request):
    if request.method == 'GET':
        return render(request, 'nueva_oferta.html')
    else:
        titulo = request.POST.get('titulo', '')
        descripcion = request.POST.get('descripcion', '')
        valido_hasta_str = request.POST.get('valido_hasta', '')
        valido_hasta = None
        if valido_hasta_str:
            valido_hasta = datetime.datetime.strptime(valido_hasta_str, '%d/%m/%Y').date()
        descuento = request.POST.get('descuento', '')
        isPorcentage = True if request.POST.get('tipo_descuento', '') == u'%' else False
        estado = 1 if request.POST.get('estado', '') == u'Activado' else 0
        oferta = Oferta.objects.create(titulo=titulo, descripcion=descripcion,
                                       estado=estado, valido_hasta=valido_hasta)
        product_names = [value for key, value in request.POST.dict().iteritems() if key.startswith("nombre_producto-")]
        productos = Producto.objects.filter(nombre__in=product_names)
        if request.is_ajax():
            img = request.FILES.get('image')
        else:
            img = request.FILES.get('upload_field_classic')
        if img:
            oferta.imagen.save(u'oferta-%d.%s' % (oferta.id, img.content_type.split('/')[1]), img)

        if isPorcentage:
            oferta.descuento_porcentual = descuento
        else:
            oferta.descuento_numerico = descuento

        if productos.exists():
            oferta.productos.add(*list(productos))

        oferta.save()

        return redirect(ofertas_view)


def nuevo_menu_view(request):
    if request.method == 'GET':
        return render(request, 'nuevo_menu.html')
    else:
        nombre = request.POST.get('nombre', '')
        descripcion = request.POST.get('descripcion', '')
        valido_hasta_str = request.POST.get('valido_hasta', '')
        if valido_hasta_str:
            valido_hasta = datetime.datetime.strptime(valido_hasta_str, '%d/%m/%Y').date()
        precio = request.POST.get('precio', '')
        estado = 1 if request.POST.get('estado', '') == u'Activado' else 0
        menu = Menu.objects.create(nombre=nombre, descripcion=descripcion,
                                   estado=estado, precio=precio, valido_hasta=valido_hasta)
        product_names = [value for key, value in request.POST.dict().iteritems() if key.startswith("nombre_producto-")]
        productos = Producto.objects.filter(nombre__in=product_names)
        if request.is_ajax():
            img = request.FILES.get('image')
        else:
            img = request.FILES.get('upload_field_classic')
        if img:
            menu.imagen.save(u'menu-%d.%s' % (menu.id, img.content_type.split('/')[1]), img)

        if productos.exists():
            menu.productos.add(*list(productos))

        menu.save()

        return redirect(menus_view)


def handle_uploaded_file(f, id, i):
    dire = os.getcwd() + '/appwb/static/anuncios/' + str(id)
    if i == 1:
        os.mkdir(dire)
    arch = dire + '/' + str(id) + '_' + str(i) + '.jpg'
    with open(arch, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def nueva_categoria_view(request):
    if request.method == 'GET':
        return render(request, 'nueva_categoria.html')
    else:
        titulo = request.POST.get('titulo', '')
        descripcion = request.POST.get('descripcion', '')
        estado = 1 if request.POST.get('estado', '') == u'Activado' else 0
        categoria = Categoria.objects.create(nombre=titulo, descripcion=descripcion, estado=estado)
        product_names = [value for key, value in request.POST.dict().iteritems() if key.startswith("nombre_producto-")]
        productos = Producto.objects.filter(nombre__in=product_names)

        if request.is_ajax():
            img = request.FILES.get('image')
        else:
            img = request.FILES.get('upload_field_classic')
        if img:
            categoria.imagen.save(u'categoria-%d.%s' % (categoria.id, img.content_type.split('/')[1]), img)

        if productos.exists():
            categoria.productos.add(*list(productos))

        return redirect(categorias_view)


def autocomplete_id_producto(request):
    """
    View used to autocomplete the buy currency field with the corresponding currency symbol
    :param request:
    :return: Json response with the matched symbols
    """
    from django.http import JsonResponse
    if request.is_ajax():
        queryset = Producto.objects.filter(nombre=request.GET.get('search', ''))
        if queryset.count() == 0 or queryset.count() > 1:
            data = {
                'id': '--',
                'precio': '--',
                'precio_oferta': '--',
            }
        else:
            data = {
                'id': queryset[0].id,
                'precio': queryset[0].precio,
                'precio_oferta': queryset[0].precio_oferta if queryset[0].precio_oferta else '--',
            }
        return JsonResponse(data)


def autocomplete_nombre_producto(request):
    """
    View used to autocomplete the buy currency field with the corresponding currency symbol
    :param request:
    :return: Json response with the matched symbols
    """
    from django.http import JsonResponse
    if request.is_ajax():
        queryset = Producto.objects.filter(nombre__startswith=request.GET.get('search', ''))
        list = []
        for i in queryset:
            list.append(i.nombre)
        data = {
            'list': list,
        }
        return JsonResponse(data)


def editar_pedido_view(request, pedido_pk):
    pedido = get_object_or_404(Pedido, pk=pedido_pk)
    ofertas = pedido.ofertapedido_set.all()
    menus = pedido.menupedido_set.all()
    productos = pedido.productopedido_set.all()
    if request.method == 'GET':
        estados = list(STATES_STR)
        alumnos = pedido.ordenante.all()
        statelogs = StateLog.objects.for_(pedido)
        return render(request, 'editar_pedido.html', {'pedido': pedido, 'alumnos': alumnos, 'ofertas': ofertas,
                                                      'menus': menus, 'productos': productos, 'statelogs': statelogs,
                                                      'estados': estados})
    else:
        estado = request.POST.get('estado', '')

        print request.POST

        if pedido.estado != estado:
            pedido.estado = estado

        for oferta in ofertas:
            form_quantity = request.POST.get('oferta-pedido-cantidad-' + str(oferta.id), '')
            if form_quantity == u'0':
                oferta.delete()
            elif not oferta.quantity == form_quantity:
                oferta.quantity = form_quantity
                oferta.save()

        for menu in menus:
            form_quantity = request.POST.get('menu-pedido-cantidad-' + str(menu.id), '')
            if form_quantity == u'0':
                menu.delete()
            elif not menu.quantity == form_quantity:
                menu.quantity = form_quantity
                menu.save()

        for producto in productos:
            form_quantity = request.POST.get('producto-pedido-cantidad-' + str(producto.id), '')
            if form_quantity == u'0':
                producto.delete()
            elif not producto.quantity == form_quantity:
                producto.quantity = form_quantity
                producto.save()

        pedido.save()

        return redirect(pedido_view, pedido_pk=pedido.id)


def test_view(request):
    return render(request, 'test.html')


def ofertas_view(request):
    ofertas = Oferta.objects.all()
    return render(request, 'ofertas.html', {'ofertas': ofertas})


def menus_view(request):
    menus = Menu.objects.all()
    return render(request, 'menus.html', {'menus': menus})


def categorias_view(request):
    categorias = Categoria.objects.all()
    return render(request, 'categorias.html', {'categorias': categorias})


def productos_view(request):
    productos = Producto.objects.all()
    return render(request, 'productos.html', {'productos': productos})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get('customer[username]', '')
        password = request.POST.get('customer[password]', '')
        user = authenticate(username=username, password=password)
        if not user:
            return render(request, 'login.html', {'login_incorrect': True})
        else:
            login(request, user)
            return redirect(index)

    if request.user.is_authenticated and not request.user.is_anonymous():
        return redirect(index)
    else:
        return render(request, 'login.html', {'login_incorrect': False})


def reset_password_view(request):
    return redirect(index)


def register_view(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    else:
        user = User()
        user.name = request.POST.get('empleado[first_name]', ' ')
        user.last_name = request.POST.get('empleado[last_name]', ' ')
        user.email = request.POST.get('empleado[email]', ' ')
        user.set_password(request.POST.get('empleado[password]', ' '))
        user.save()
        empleado = Empleado(name=user.name, apellido=user.last_name,
                            user=user)
        empleado.save()

        return redirect(index)
