"""cafetering_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from cafetering_app import views, settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

app_name = 'cafetering_app'

urlpatterns = [
    url(r'^$', views.login_view, name='login_view'),
    url(r'^login$', views.login_view, name='login_view'),
    url(r'^reset_password$', views.reset_password_view, name='reset_password_view'),
    url(r'^admin/', admin.site.urls),
    url(r'^index$', views.index, name='index'),
    url(r'^pedidos$', views.pedidos_view, name='pedidos_view'),

    url(r'^(?i)ver-pedido/(?P<pedido_pk>[0-9]+)/$', views.pedido_view, name='pedido_view'),
    url(r'^(?i)ver-oferta/(?P<oferta_pk>[0-9]+)/$', views.oferta_view, name='oferta_view'),
    url(r'^(?i)ver-menu/(?P<menu_pk>[0-9]+)/$', views.menu_view, name='menu_view'),
    url(r'^(?i)ver-categoria/(?P<categoria_pk>[0-9]+)/$', views.categoria_view, name='categoria_view'),
    url(r'^(?i)ver-producto/(?P<producto_pk>[0-9]+)/$', views.producto_view, name='producto_view'),

    url(r'^nueva-oferta/?$', views.nueva_oferta_view, name='nueva_oferta_view'),
    url(r'^nuevo-menu/?$', views.nuevo_menu_view, name='nuevo_menu_view'),
    url(r'^nueva-categoria/?$', views.nueva_categoria_view, name='nueva_categoria_view'),
    url(r'^nuevo-producto/?$', views.nuevo_producto_view, name='nuevo_producto_view'),

    url(r'^editar-pedido/(?P<pedido_pk>[0-9]+)/$', views.editar_pedido_view, name='editar_pedido_view'),
    url(r'^editar-oferta/(?P<oferta_pk>[0-9]+)/$', views.editar_oferta_view, name='editar_oferta_view'),
    url(r'^editar-menu/(?P<menu_pk>[0-9]+)/$', views.editar_menu_view, name='editar_menu_view'),
    url(r'^editar-producto/(?P<producto_pk>[0-9]+)/$', views.editar_producto_view, name='editar_producto_view'),
    url(r'^editar-categoria/(?P<categoria_pk>[0-9]+)/$', views.editar_categoria_view, name='editar_categoria_view'),

    url(r'^eliminar-pedido/(?P<pedido_pk>[0-9]+)/?$', views.eliminar_pedido_view, name='eliminar_pedido_view'),
    url(r'^eliminar-oferta/(?P<oferta_pk>[0-9]+)/?$', views.eliminar_oferta_view, name='eliminar_oferta_view'),
    url(r'^eliminar-menu/(?P<menu_pk>[0-9]+)/?$', views.eliminar_menu_view, name='eliminar_menu_view'),
    url(r'^eliminar-producto/(?P<producto_pk>[0-9]+)/?$', views.eliminar_producto_view, name='eliminar_producto_view'),
    url(r'^eliminar-categoria/(?P<categoria_pk>[0-9]+)/?$', views.eliminar_categoria_view,
        name='eliminar_categoria_view'),

    url(r'^ofertas$', views.ofertas_view, name='ofertas_view'),
    url(r'^menus$', views.menus_view, name='menus_view'),
    url(r'^productos$', views.productos_view, name='productos_view'),
    url(r'^categorias$', views.categorias_view, name='categorias_view'),
    url(r'^logout$', views.logout_view, name='logout_view'),
    url(r'^cuenta$', views.cuenta_view, name='cuenta_view'),
    url(r'^informes$', views.informes_view, name='informes_view'),
    url(r'^ayuda$', views.ayuda_view, name='ayuda_view'),
    url(r'^buscar$', views.buscar_view, name='buscar_view'),

    url(r'^pedido-preparado/(?P<pedido_pk>[0-9]+)/?$', views.pedido_preparado_view, name='pedido_preparado_view'),
    url(r'^pedido-recogido/(?P<pedido_pk>[0-9]+)/?$', views.pedido_recogido_view, name='pedido_recogido_view'),
    url(r'^pedido-norecogido/(?P<pedido_pk>[0-9]+)/?$', views.pedido_no_recogido_view, name='pedido_no_recogido_view'),
    url(r'^test$', views.test_view, name='test_view'),

    url(r'^ajax/autocomplete_id_producto/$', views.autocomplete_id_producto, name='autocomplete_id_producto'),
    url(r'^ajax/autocomplete_nombre_producto/$', views.autocomplete_nombre_producto,
        name='autocomplete_nombre_producto'),
    url(r'^ajax/autocomplete_oferta/$', views.autocomplete_oferta_view, name='autocomplete_oferta_view'),
    url(r'^ajax/autocomplete_menu/$', views.autocomplete_menu_view, name='autocomplete_menu_view'),
    url(r'^ajax/autocomplete_nombre_alergeno/$', views.autocomplete_alergeno_view, name='autocomplete_alergeno_view'),
    url(r'^ajax/autocomplete_nombre_etiqueta/$', views.autocomplete_etiqueta_view, name='autocomplete_etiqueta_view'),
    url(r'^ajax/remove_product_from_list/$', views.remove_product_from_list, name='remove_product_from_list'),
    url(r'^ajax/reset_password/$', views.reset_password, name='reset_password'),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
