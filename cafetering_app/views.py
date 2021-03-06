import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from bos.models import *
from django.shortcuts import get_object_or_404
from django_fsm_log.models import StateLog


def logout_view(request):
    logout(request)
    return redirect(login_view)


@login_required
def index(request):
    return redirect(pedidos_view)


@login_required
def pedidos_view(request):
    from datetime import datetime, timedelta
    td = timedelta(days=300)
    from_date = datetime.now().date() - td
    end_date = datetime.now().date()
    if request.method == 'POST':

        estado_pedido = list(unicode(estado) for estado in STATES_STR)
        if request.POST.get('range_from', ''):
            from_date = datetime.strptime(request.POST.get('range_from'), '%d/%m/%Y')

        if request.POST.get('range_to', ''):
            end_date = datetime.strptime(request.POST.get('range_to'), '%d/%m/%Y') + timedelta(days=1)

        if request.POST.get('estado_pedido', '') != 'all':
            estado_pedido = request.POST.getlist('estado_pedido', '')

        pedidos = Pedido.objects.filter(fecha_creacion__range=(from_date, end_date),
                                        estado__in=estado_pedido)

        if request.POST.get('action', '') == "exportar":
            archivo = 'cafetering_app/media/reports/reporte.xlsx'

            import xlsxwriter
            from django.http import HttpResponse

            workbook = xlsxwriter.Workbook(archivo)
            worksheet = workbook.add_worksheet()
            worksheet.write(0, 0, 'Pedido ID')
            worksheet.write(0, 1, 'Estado')
            worksheet.write(0, 2, 'Recogida estimada')
            worksheet.write(0, 3, 'Recogido')
            worksheet.write(0, 4, 'Importe')
            for i, pedido in enumerate(pedidos):
                row = ["#%d" % pedido.id, pedido.get_estado_display(),
                       pedido.recogida_estimada.strftime("%d/%m/%y %H:%M:%S") if pedido.recogida_estimada else '---',
                       pedido.fecha_recogida.strftime("%d/%m/%y %H:%M:%S") if pedido.fecha_recogida else '---',
                       pedido.importe]
                col = 0
                for value in row:
                    worksheet.write(i + 1, col, value)
                    col += 1

            workbook.close()
            f = open('cafetering_app/media/reports/reporte.xlsx', 'r')
            pdf_contents = f.read()
            f.close()
            response = HttpResponse(pdf_contents, content_type='application/xlsx')
            response['Content-Disposition'] = 'attachment; filename="reporte.xlsx"'
            return response

        return render(request, 'pedidos.html',
                      {'pedidos': pedidos, 'estado_pedido': estado_pedido, 'estados': STATES_STR,
                       'from_date': from_date,
                       'end_date': end_date - timedelta(days=1), 'is_filtered': True})

    pedidos = Pedido.objects.all()
    return render(request, 'pedidos.html', {'pedidos': pedidos,
                                            'estados': STATES_STR, 'is_filtered': False, 'from_date': from_date,
                                            'end_date': end_date})


@login_required
def pedido_view(request, pedido_pk):
    pedido = get_object_or_404(Pedido, pk=pedido_pk)
    alumnos = pedido.ordenante.all()
    ofertas = pedido.ofertapedido_set.all()
    menus = pedido.menupedido_set.all()
    productos = pedido.productopedido_set.all()
    statelogs = StateLog.objects.for_(pedido)
    return render(request, 'pedido.html', {'pedido': pedido, 'alumnos': alumnos, 'ofertas': ofertas,
                                           'menus': menus, 'productos': productos, 'statelogs': statelogs})


@login_required
def producto_view(request, producto_pk):
    producto = get_object_or_404(Producto, pk=producto_pk)
    alergenos = producto.alergenos.all()
    etiquetas = producto.etiquetas.all()
    return render(request, "ver-producto.html",
                  {'producto': producto, "alergenos": alergenos, "etiquetas": etiquetas})


@login_required
def categoria_view(request, categoria_pk):
    categoria = get_object_or_404(Categoria, pk=categoria_pk)
    productos = categoria.productos.all()
    return render(request, "ver-categoria.html", {'categoria': categoria, 'productos': productos})


@login_required
def eliminar_categoria_view(request, categoria_pk):
    obj = get_object_or_404(Categoria, pk=categoria_pk)
    obj.delete()
    return redirect(categorias_view)


@login_required
def eliminar_producto_view(request, producto_pk):
    obj = get_object_or_404(Producto, pk=producto_pk)
    obj.delete()
    return redirect(productos_view)


@login_required
def eliminar_pedido_view(request, pedido_pk):
    obj = get_object_or_404(Pedido, pk=pedido_pk)
    obj.cancelar(by=request.user)
    obj.observaciones = request.POST.get("descripcion", "")
    obj.save()
    return redirect(pedidos_view)


@login_required
def eliminar_menu_view(request, menu_pk):
    obj = get_object_or_404(Menu, pk=menu_pk)
    obj.delete()
    return redirect(menus_view)


@login_required
def eliminar_oferta_view(request, oferta_pk):
    obj = get_object_or_404(Oferta, pk=oferta_pk)
    obj.delete()
    return redirect(ofertas_view)


@login_required
def oferta_view(request, oferta_pk):
    oferta = get_object_or_404(Oferta, pk=oferta_pk)
    productos = oferta.ofertaproducto_set.all()
    return render(request, "ver-oferta.html", {'oferta': oferta, 'productos': productos})


@login_required
def menu_view(request, menu_pk):
    menu = get_object_or_404(Menu, pk=menu_pk)
    productos = menu.menuproducto_set.all()
    return render(request, "ver-menu.html", {'menu': menu, 'productos': productos})


@login_required
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
        product_names = [(key.split("nombre_producto-")[1], value) for key, value in request.POST.dict().iteritems()
                         if key.startswith("nombre_producto-")]
        for row, name in product_names:
            producto = Producto.objects.filter(nombre=name)
            if producto.exists() and producto.count() == 1:
                OfertaProducto.objects.create(producto=producto[0],
                                              oferta=oferta,
                                              quantity=int(request.POST.get('cantidad_producto-%s' % row, '0')))

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

        oferta.cafeteria = Empleado.objects.get(user=request.user).cafeteria.first()

        oferta.save()

        return redirect(ofertas_view)


@login_required
def nuevo_producto_view(request):
    if request.method == 'GET':
        return render(request, 'nuevo_producto.html')
    else:
        nombre = request.POST.get('nombre', '')
        descripcion = request.POST.get('descripcion', '')
        grasas = request.POST.get('grasas', '0').replace(",", ".")
        calorias = request.POST.get('calorias', '0').replace(",", ".")
        precio = request.POST.get('precio_producto', '0').replace(",", ".")
        estado = 1 if request.POST.get('estado', '') == u'Activado' else 0
        producto = Producto.objects.create(nombre=nombre, descripcion=descripcion,
                                           estado=estado, grasas_saturadas=grasas,
                                           precio=precio, calorias=calorias)
        nombre_alergenos = [value for key, value in request.POST.dict().iteritems() if
                            key.startswith("nombre_alergeno-")]
        nombre_etiquetas = [value for key, value in request.POST.dict().iteritems() if
                            key.startswith("nombre_etiquetas-")]

        alergenos = []
        for algr in nombre_alergenos:
            alergenos.append(Alergeno.objects.get_or_create(nombre=algr)[0])

        etiquetas = []
        for etq in nombre_etiquetas:
            etiquetas.append(Etiqueta.objects.get_or_create(nombre=etq)[0])

        if len(alergenos) > 0:
            producto.alergenos.clear()
            producto.alergenos.add(*alergenos)

        if len(etiquetas) > 0:
            producto.etiquetas.clear()
            producto.etiquetas.add(*etiquetas)

        if request.is_ajax():
            img = request.FILES.get('image')
        else:
            img = request.FILES.get('upload_field_classic')

        if img:
            producto.imagen.save(u'producto-%d.%s' % (producto.id, img.content_type.split('/')[1]), img)

        producto.cafeteria = Empleado.objects.get(user=request.user).cafeteria.first()

        producto.save()

        return redirect(productos_view)


@login_required
def nuevo_menu_view(request):
    if request.method == 'GET':
        return render(request, 'nuevo_menu.html')
    else:
        nombre = request.POST.get('nombre', '')
        descripcion = request.POST.get('descripcion', '')
        valido_hasta_str = request.POST.get('valido_hasta', '')
        valido_hasta = None
        if valido_hasta_str:
            valido_hasta = datetime.datetime.strptime(valido_hasta_str, '%d/%m/%Y').date()
        precio = request.POST.get('precio', '').replace(",", ".")
        estado = 1 if request.POST.get('estado', '') == u'Activado' else 0
        menu = Menu.objects.create(nombre=nombre, descripcion=descripcion,
                                   estado=estado, precio=precio, valido_hasta=valido_hasta)
        product_names = [(key.split("nombre_producto-")[1], value) for key, value in request.POST.dict().iteritems()
                         if key.startswith("nombre_producto-")]
        for row, name in product_names:
            producto = Producto.objects.filter(nombre=name)
            if producto.exists() and producto.count() == 1:
                MenuProducto.objects.create(producto=producto[0],
                                            menu=menu,
                                            quantity=int(request.POST.get('cantidad_producto-%s' % row, '0')))
        if request.is_ajax():
            img = request.FILES.get('image')
        else:
            img = request.FILES.get('upload_field_classic')
        if img:
            menu.imagen.save(u'menu-%d.%s' % (menu.id, img.content_type.split('/')[1]), img)

        menu.cafeteria = Empleado.objects.get(user=request.user).cafeteria.first()
        menu.save()

        return redirect(menus_view)


@login_required
def nueva_categoria_view(request):
    if request.method == 'GET':
        return render(request, 'nueva_categoria.html')
    else:
        titulo = request.POST.get('titulo', '')
        descripcion = request.POST.get('descripcion', '')
        estado = 1 if request.POST.get('estado', '') == u'Activado' else 0
        cafeteria = Empleado.objects.get(user=request.user).cafeteria.first()
        categoria = Categoria.objects.create(nombre=titulo, descripcion=descripcion, estado=estado, cafeteria=cafeteria)
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


@login_required
def autocomplete_id_producto(request):
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


@login_required
def remove_product_from_list(request):
    from django.http import JsonResponse
    if request.is_ajax():
        producto = get_object_or_404(Producto, pk=int(request.GET.get('id', '')))
        object_name = request.GET.get('object_name', '')
        object_pk = request.GET.get('object_pk', '')
        if object_name == 'categoria':
            obj = Categoria.objects.get(pk=object_pk)
            obj.productos.remove(producto)
        elif object_name == 'oferta':
            OfertaProducto.objects.get(oferta__id=object_pk, producto=producto).delete()
        elif object_name == 'menu':
            obj = Menu.objects.get(pk=object_pk)
        elif object_name == 'pedido':
            obj = Pedido.objects.get(pk=object_pk)
            obj.productos.remove(producto)

        data = {}
        return JsonResponse(data)


@login_required
def autocomplete_nombre_producto(request):
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


@login_required
def autocomplete_menu_view(request):
    from django.http import JsonResponse
    if request.is_ajax():
        queryset = Menu.objects.filter(nombre__icontains=request.GET.get('search', ''))
        list = []
        for i in queryset:
            list.append(i.nombre)
        data = {
            'list': list,
        }
        return JsonResponse(data)


@login_required
def autocomplete_oferta_view(request):
    from django.http import JsonResponse
    if request.is_ajax():
        queryset = Oferta.objects.filter(titulo__icontains=request.GET.get('search', ''))
        list = []
        for i in queryset:
            list.append(i.titulo)
        data = {
            'list': list,
        }
        return JsonResponse(data)


@login_required
def autocomplete_etiqueta_view(request):
    from django.http import JsonResponse
    if request.is_ajax():
        queryset = Etiqueta.objects.filter(nombre__icontains=request.GET.get('search', ''))
        list = []
        for i in queryset:
            list.append(i.nombre)
        data = {
            'list': list,
        }
        return JsonResponse(data)


@login_required
def autocomplete_alergeno_view(request):
    from django.http import JsonResponse
    if request.is_ajax():
        queryset = Alergeno.objects.filter(nombre__icontains=request.GET.get('search', ''))
        list = []
        for i in queryset:
            list.append(i.nombre)
        data = {
            'list': list,
        }
        return JsonResponse(data)


@login_required
def editar_producto_view(request, producto_pk):
    producto = get_object_or_404(Producto, pk=producto_pk)
    if request.method == 'GET':
        alergenos = producto.alergenos.all()
        etiquetas = producto.etiquetas.all()
        return render(request, "editar_producto.html",
                      {'producto': producto, "alergenos": alergenos, "etiquetas": etiquetas})
    else:
        producto.nombre = request.POST.get('nombre', '')
        producto.descripcion = request.POST.get('descripcion', '')
        producto.grasas_saturadas = request.POST.get('grasas', '0').replace(",", ".") \
            if not request.POST.get('grasas', '0') == u'None' else None
        producto.calorias = request.POST.get('calorias', '0').replace(",", ".") \
            if not request.POST.get('calorias', '0') == u'None' else None
        producto.precio = request.POST.get('precio_producto', '0').replace(",", ".")
        producto.estado = 1 if request.POST.get('estado', '') == u'Activado' else 0

        nombre_alergenos = [value for key, value in request.POST.dict().iteritems() if
                            key.startswith("nombre_alergeno-")]
        nombre_etiquetas = [value for key, value in request.POST.dict().iteritems() if
                            key.startswith("nombre_etiquetas-")]

        alergenos = []
        for algr in nombre_alergenos:
            alergenos.append(Alergeno.objects.get_or_create(nombre=algr)[0])

        etiquetas = []
        for etq in nombre_etiquetas:
            etiquetas.append(Etiqueta.objects.get_or_create(nombre=etq)[0])

        if len(alergenos) > 0:
            producto.alergenos.clear()
            producto.alergenos.add(*alergenos)

        if len(etiquetas) > 0:
            producto.etiquetas.clear()
            producto.etiquetas.add(*etiquetas)

        img = request.FILES.get('upload_field_classic', '')

        if img:
            producto.imagen.save(u'producto-%d.%s' % (producto.id, img.content_type.split('/')[1]), img)

        producto.save()

        return redirect(producto_view, producto_pk)


@login_required
def editar_oferta_view(request, oferta_pk):
    if request.method == 'GET':
        oferta = get_object_or_404(Oferta, pk=oferta_pk)
        productos = oferta.ofertaproducto_set.all()
        return render(request, "editar_oferta.html", {'oferta': oferta, 'productos': productos})
    else:
        titulo = request.POST.get('titulo', '')
        descripcion = request.POST.get('descripcion', '')
        valido_hasta_str = request.POST.get('valido_hasta', '')
        valido_hasta = None
        if valido_hasta_str:
            valido_hasta = datetime.datetime.strptime(valido_hasta_str, '%d/%m/%Y').date()
        descuento = request.POST.get('descuento', '').replace(',', '.')
        isPorcentage = True if request.POST.get('tipo_descuento', '') == u'%' else False
        estado = 1 if request.POST.get('estado', '') == u'Activado' else 0
        oferta = Oferta.objects.get(pk=oferta_pk)
        oferta.titulo = titulo
        oferta.descripcion = descripcion
        oferta.estado = estado
        oferta.valido_hasta = valido_hasta

        product_names = [(key.split("nombre_producto-")[1], value) for key, value in request.POST.dict().iteritems()
                         if key.startswith("nombre_producto-")]
        for row, name in product_names:
            producto = Producto.objects.filter(nombre=name)
            if producto.exists() and producto.count() == 1:
                OfertaProducto.objects.update_or_create(producto=producto[0],
                                                        oferta=oferta,
                                                        quantity=int(
                                                            request.POST.get('cantidad_producto-%s' % row, '0')))

        if request.FILES.get('upload_field_classic', ''):
            img = request.FILES.get('upload_field_classic')
            oferta.imagen.save(u'oferta-%d.%s' % (oferta.id, img.content_type.split('/')[1]), img)

        if isPorcentage:
            oferta.descuento_porcentual = descuento
        else:
            oferta.descuento_numerico = descuento

        oferta.save()

        return redirect(oferta_view, oferta_pk)


@login_required
def editar_pedido_view(request, pedido_pk):
    from datetime import datetime

    pedido = get_object_or_404(Pedido, pk=pedido_pk)
    ofertas = pedido.ofertapedido_set.all()
    menus = pedido.menupedido_set.all()
    productos = pedido.productopedido_set.all()
    if request.method == 'GET':
        estados = list(STATES_STR)
        alumnos = pedido.ordenante.all()
        return render(request, 'editar_pedido.html', {'pedido': pedido, 'alumnos': alumnos, 'ofertas': ofertas,
                                                      'menus': menus, 'productos': productos, 'estados': estados})
    else:
        estado = request.POST.get('estado', '')

        recogida_estimada = request.POST.get('recogida_estimada', '')

        if pedido.estado != estado:
            pedido.set_estado(estado, user=request.user)

        if pedido.recogida_estimada != recogida_estimada:
            pedido.recogida_estimada = datetime.strptime(recogida_estimada.replace('T', ' '), '%Y-%m-%d %H:%M')

        for oferta in ofertas:
            form_quantity = int(request.POST.get('oferta-pedido-cantidad-id-' + str(oferta.oferta.id), '0'))
            if form_quantity == 0:
                oferta.delete()
            elif not oferta.quantity == form_quantity:
                oferta.quantity = form_quantity
                oferta.save()

        for menu in menus:
            form_quantity = int(request.POST.get('menu-pedido-cantidad-id-' + str(menu.menu.id), '0'))
            if form_quantity == 0:
                menu.delete()
            elif not menu.quantity == form_quantity:
                menu.quantity = form_quantity
                menu.save()

        for producto in productos:
            form_quantity = int(request.POST.get('producto-pedido-cantidad-id-' + str(producto.id), '0'))
            if form_quantity == 0:
                producto.delete()
            elif not producto.quantity == form_quantity:
                producto.quantity = form_quantity
                producto.save()

        nuevos_productos = [(key[-1], value) for key, value in request.POST.dict().iteritems() if
                            key.startswith("nombre_producto-")]

        ofertas = [(key[-1], value) for key, value in request.POST.dict().iteritems() if
                   key.startswith("nombre_oferta-")]

        menus = [(key[-1], value) for key, value in request.POST.dict().iteritems() if key.startswith("nombre_menu-")]

        for row, name in ofertas:
            oferta = Oferta.objects.filter(titulo=name)
            if oferta.exists():
                oferta = oferta[0]
                cantidad = request.POST.get('cantidad_oferta-%s' % row, '0')
                if not OfertaPedido.objects.filter(pedido=pedido, oferta=oferta).exists():
                    OfertaPedido.objects.create(pedido=pedido, oferta=oferta, quantity=int(cantidad),
                                                precio_oferta=oferta.precio_oferta)
                else:
                    op = OfertaPedido.objects.get(pedido=pedido, oferta=oferta)
                    op.quantity += int(cantidad)
                    op.save()

        for row, name in menus:
            menu = Menu.objects.filter(nombre=name)
            if menu.exists():
                menu = menu[0]
                cantidad = request.POST.get('cantidad_menu-%s' % row, '0')
                if not MenuPedido.objects.filter(pedido=pedido, menu=menu).exists():
                    MenuPedido.objects.create(pedido=pedido, menu=menu, quantity=int(cantidad),
                                              precio_menu=menu.precio)
                else:
                    op = MenuPedido.objects.get(pedido=pedido, menu=menu)
                    op.quantity += int(cantidad)
                    op.save()

        for row, name in nuevos_productos:
            producto = Producto.objects.filter(nombre=name)
            if producto.exists():
                producto = producto[0]
                cantidad = request.POST.get('row-producto-pedido-cantidad-%s' % row, '0')
                if not ProductoPedido.objects.filter(pedido=pedido, producto=producto).exists():
                    ProductoPedido.objects.create(pedido=pedido, producto=producto, quantity=int(cantidad),
                                                  precio_producto=producto.precio)
                else:
                    op = ProductoPedido.objects.get(pedido=pedido, producto=producto)
                    op.quantity += int(cantidad)
                    op.save()

        pedido.save()

        return redirect(pedido_view, pedido_pk=pedido.id)


@login_required
def editar_menu_view(request, menu_pk):
    if request.method == 'GET':
        menu = get_object_or_404(Menu, pk=menu_pk)
        productos = menu.menuproducto_set.all()
        return render(request, 'editar_menu.html', {'menu': menu, 'productos': productos})
    else:
        nombre = request.POST.get('nombre', '')
        descripcion = request.POST.get('descripcion', '')
        valido_hasta_str = request.POST.get('valido_hasta', '')
        valido_hasta = None
        if valido_hasta_str:
            valido_hasta = datetime.datetime.strptime(valido_hasta_str, '%d/%m/%Y').date()
        precio = request.POST.get('precio', '').replace(',', '.')
        estado = 1 if request.POST.get('estado', '') == u'Activado' else 0

        menu = Menu.objects.get(pk=int(menu_pk))
        menu.nombre = nombre
        menu.descripcion = descripcion
        menu.estado = estado
        menu.precio = precio
        menu.valido_hasta = valido_hasta

        product_names = [(key.split("nombre_producto-")[1], value) for key, value in request.POST.dict().iteritems()
                         if key.startswith("nombre_producto-")]
        for row, name in product_names:
            producto = Producto.objects.filter(nombre=name)
            if producto.exists() and producto.count() == 1:
                MenuProducto.objects.update_or_create(producto=producto[0],
                                                      menu=menu,
                                                      quantity=int(request.POST.get('cantidad_producto-%s' % row, '0')))

        img = request.FILES.get('upload_field_classic', '')
        if img:
            menu.imagen.save(u'menu-%d.%s' % (menu.id, img.content_type.split('/')[1]), img)

        menu.save()

        return redirect(menu_view, menu_pk)


@login_required
def editar_categoria_view(request, categoria_pk):
    if request.method == 'GET':
        categoria = get_object_or_404(Categoria, pk=categoria_pk)
        productos = categoria.productos.all()
        return render(request, 'editar-categoria.html', {'categoria': categoria, 'productos': productos})
    else:
        nombre = request.POST.get('titulo', '')
        descripcion = request.POST.get('descripcion', '')
        estado = 1 if request.POST.get('estado', '') == u'Activado' else 0

        categoria = Categoria.objects.get(pk=int(categoria_pk))
        categoria.nombre = nombre
        categoria.descripcion = descripcion
        categoria.estado = estado

        product_names = [value for key, value in request.POST.dict().iteritems() if key.startswith("nombre_producto-")]
        productos = Producto.objects.filter(nombre__in=product_names)
        img = request.FILES.get('upload_field_classic', '')
        if img:
            categoria.imagen.save(u'categoria-%d.%s' % (categoria.id, img.content_type.split('/')[1]), img)

        if productos.exists():
            categoria.productos.add(*list(productos))

        categoria.save()

        return redirect(categoria_view, categoria_pk)


def test_view(request):
    return render(request, 'base.html')


@login_required
def ayuda_view(request):
    if request.method == 'POST':
        return render(request, 'contact.html', {'enviado': True})
    return render(request, 'contact.html', {'enviado': False})


@login_required
def buscar_view(request):
    from itertools import chain
    if request.method == 'POST':
        search_term = request.POST.get('search_term_form', '')
        result_list = []
        if u'#' in search_term or search_term.isdigit():
            ide = search_term.replace(u'#', u'')
            pedidos = Pedido.objects.filter(pk=ide)
            ofertas = Oferta.objects.filter(pk=ide)
            menus = Menu.objects.filter(pk=ide)
            categorias = Categoria.objects.filter(pk=ide)
            productos = Producto.objects.filter(pk=ide)
            if pedidos or ofertas or menus or categorias or productos:
                result_list.extend(list(chain(pedidos, ofertas, menus, categorias, productos)))
        else:
            ofertas = Oferta.objects.filter(titulo__icontains=search_term)
            menus = Menu.objects.filter(nombre__icontains=search_term)
            categorias = Categoria.objects.filter(nombre__icontains=search_term)
            productos = Producto.objects.filter(nombre__icontains=search_term)
            if ofertas or menus or categorias or productos:
                result_list.extend(list(chain(ofertas, menus, categorias, productos)))
        print result_list
        return render(request, 'buscar.html', {'search_term': search_term, 'result_list': result_list})

    return render(request, 'buscar.html', {'search_term': ''})


@login_required
def informes_view(request):
    from datetime import datetime, timedelta
    from cafetering_app.utiles.reports import generate_pie_chart, generate_orders_report

    td = timedelta(days=300)
    from_date = datetime.now().date() - td
    end_date = datetime.now().date()
    estado_pedido = list(unicode(estado) for estado in STATES_STR)
    estados = [0, 1]

    if request.method == 'POST':
        if request.POST.get('range_from', ''):
            from_date = datetime.strptime(request.POST.get('range_from'), '%d/%m/%Y')

        if request.POST.get('range_to', ''):
            end_date = datetime.strptime(request.POST.get('range_to'), '%d/%m/%Y') + timedelta(days=1)

        if request.POST.get('estado_pedido', '') != 'all':
            estado_pedido = request.POST.getlist('estado_pedido', '')

        if request.POST.get('estado_objecto', '') != 'all':
            estados = [int(request.POST.get('estado_objecto', '1'))]

        if request.POST.get('recurso', '') == u'pie_chart':
            generate_pie_chart(from_date, end_date, estado_pedido, estados)

        elif request.POST.get('recurso', '') == u'orders':
            generate_orders_report(from_date, end_date, estado_pedido)
        else:
            pass
        return render(request, 'informes.html',
                      {'estados': estado_pedido, 'from_date': from_date, 'end_date': end_date - timedelta(days=1),
                       'showPics': True,
                       'recurso': request.POST.get('recurso'), 'estado_pedido': estado_pedido,
                       'estados_select': 2 if [0, 1] == estados else estados[0]})
    else:
        return render(request, 'informes.html',
                      {'estados': STATES_STR, 'from_date': from_date, 'end_date': end_date, 'showPics': False})


@login_required()
def pedido_preparado_view(request, pedido_pk):
    obj = get_object_or_404(Pedido, pk=pedido_pk)
    obj.preparado(by=request.user)
    obj.save()
    return redirect(pedidos_view)


@login_required()
def pedido_recogido_view(request, pedido_pk):
    obj = get_object_or_404(Pedido, pk=pedido_pk)
    obj.recogido(by=request.user)
    obj.save()
    return redirect(pedidos_view)


@login_required()
def pedido_no_recogido_view(request, pedido_pk):
    obj = get_object_or_404(Pedido, pk=pedido_pk)
    obj.no_recogido(by=request.user)
    obj.observaciones = request.POST.get("descripcion", "")
    obj.save()
    return redirect(pedidos_view)


@login_required()
def cuenta_view(request):
    user = request.user
    empleado = Empleado.objects.get(user=user)
    cafeterias = empleado.cafeteria.all()
    return render(request, 'account.html', {'user': user, 'empleado': empleado, 'cafeterias': cafeterias})


@login_required()
def reset_password(request):
    from django.http import JsonResponse
    return JsonResponse({})


@login_required
def ofertas_view(request):
    ofertas = Oferta.objects.all()
    return render(request, 'ofertas.html', {'ofertas': ofertas})


@login_required
def menus_view(request):
    menus = Menu.objects.all()
    return render(request, 'menus.html', {'menus': menus})


@login_required
def categorias_view(request):
    categorias = Categoria.objects.all()
    return render(request, 'categorias.html', {'categorias': categorias})


@login_required
def productos_view(request):
    productos = Producto.objects.all()
    return render(request, 'productos.html', {'productos': productos})


def login_view(request):
    if request.method == "POST":
        if request.POST.get('action', '') == u'Test Login':
            user = authenticate(username='test_user', password='po0231532')
            login(request, user)
            return redirect(index)
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


@login_required
def reset_password_view(request):
    return redirect(index)
