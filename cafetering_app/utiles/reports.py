from django.db.models import Q
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from django.db.models import Sum, Count
from bos.models import MenuPedido, ProductoPedido, OfertaPedido, Pedido


def generate_pie_chart(from_date, end_date, estado_pedido, estados):
    query = Q(pedido__fecha_creacion__range=(from_date, end_date), pedido__estado__in=estado_pedido)

    mps = MenuPedido.objects.filter(query | Q(menu__estado__in=estados)).values(
        'menu__nombre').annotate(Sum('quantity'))
    ops = OfertaPedido.objects.filter(query | Q(oferta__estado__in=estados)).values(
        'oferta__titulo').annotate(Sum('quantity'))
    pps = ProductoPedido.objects.filter(query | Q(producto__estado__in=estados)).values(
        'producto__nombre').annotate(Sum('quantity'))
    cps = ProductoPedido.objects.filter(query | Q(producto__estado__in=estados)).values(
        'producto__categoria__nombre').annotate(Sum('quantity'))
    if mps:
        labels = []
        sizes = []
        for mp in mps:
            labels.append(mp['menu__nombre'])
            sizes.append(mp['quantity__sum'])

        plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')
        plt.title('Menus vendidos')
        plt.savefig('cafetering_app/media/graficos/menupedido.jpg')
        plt.close('all')

    if ops:
        labels = []
        sizes = []
        for op in ops:
            labels.append(op['oferta__titulo'])
            sizes.append(op['quantity__sum'])

        plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')
        plt.title('Ofertas vendidas')
        plt.savefig('cafetering_app/media/graficos/ofertapedido.jpg')
        plt.close('all')

    if pps:
        labels = []
        sizes = []
        for pp in pps:
            labels.append(pp['producto__nombre'])
            sizes.append(pp['quantity__sum'])

        plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')
        plt.title('Productos vendidos')
        plt.savefig('cafetering_app/media/graficos/productopedido.jpg')
        plt.close('all')

    if cps:
        labels = []
        sizes = []
        for cp in cps:
            labels.append(cp['producto__categoria__nombre'])
            sizes.append(cp['quantity__sum'])
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')
        plt.title('Ventas por categorias')
        plt.savefig('cafetering_app/media/graficos/categoriapedido.jpg')
        plt.close('all')


def generate_orders_report(from_date, end_date, estado_pedido):
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.ticker import MaxNLocator

    stats = Pedido.objects.filter(fecha_creacion__range=(from_date, end_date),
                                  estado__in=estado_pedido).values('estado').annotate(Count('id'))
    estado_pedido_ord = []
    data = []

    for stat in stats:
        estado_pedido_ord.append(stat['estado'])
        data.append(stat['id__count'])

    np.random.seed(42)
    ax = plt.subplot(111)
    width = 0.3
    bins = map(lambda x: x - width / 2, range(1, len(data) + 1))
    ax.bar(bins, data, width=width)
    ax.set_xticks(map(lambda x: x, range(1, len(data) + 1)))
    ax.set_xticklabels(estado_pedido_ord, rotation=45, rotation_mode="anchor", ha="right")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.subplots_adjust(bottom=0.15)
    plt.title('Pedidos por estado')
    plt.savefig('cafetering_app/media/graficos/pedidosestado.jpg')
    plt.close('all')

    estado_pedido_ord = []
    data = []
    stats = Pedido.objects.filter(fecha_creacion__range=(from_date, end_date),
                                  estado__in=estado_pedido).extra(
        select={'day': "date( fecha_creacion )"}).values('day').annotate(Count('id'))

    for stat in stats:
        if stat['day'].__class__.__name__ == 'unicode':
            estado_pedido_ord.append(datetime.strptime(stat['day'], '%Y-%m-%d').strftime('%d/%m/%y'))
        else:
            estado_pedido_ord.append(stat['day'].strftime('%d/%m/%y'))

        data.append(stat['id__count'])

    np.random.seed(42)
    ax = plt.subplot(111)
    bins = map(lambda x: x - width / 2, range(1, len(data) + 1))
    ax.bar(bins, data, width=width)
    ax.set_xticks(map(lambda x: x, range(1, len(data) + 1)))
    ax.set_xticklabels(estado_pedido_ord, rotation=45, rotation_mode="anchor", ha="right")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.subplots_adjust(bottom=0.15)
    plt.title('Pedidos por fecha')
    plt.savefig('cafetering_app/media/graficos/pedidosporfecha.jpg')
    plt.close('all')
