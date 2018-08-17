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

    url(r'^ver-pedido/(?P<pedido_pk>[0-9]+)/$', views.pedido_view, name='pedido_view'),
    url(r'^ver-oferta/(?P<oferta_pk>[0-9]+)/$', views.oferta_view, name='oferta_view'),
    url(r'^ver-menu/(?P<menu_pk>[0-9]+)/$', views.menu_view, name='menu_view'),
    url(r'^ver-categoria/(?P<categoria_pk>[0-9]+)/$', views.categoria_view, name='categoria_view'),

    url(r'^nueva-oferta/?$', views.nueva_oferta_view, name='nueva_oferta_view'),
    url(r'^nuevo-menu/?$', views.nuevo_menu_view, name='nuevo_menu_view'),
    url(r'^nueva-categoria/?$', views.nueva_categoria_view, name='nueva_categoria_view'),

    url(r'^editar-pedido/(?P<pedido_pk>[0-9]+)/$', views.editar_pedido_view, name='editar_pedido_view'),
    url(r'^ofertas$', views.ofertas_view, name='ofertas_view'),
    url(r'^menus$', views.menus_view, name='menus_view'),
    url(r'^productos$', views.productos_view, name='productos_view'),
    url(r'^categorias$', views.categorias_view, name='categorias_view'),
    url(r'^logout$', views.logout_view, name='logout_view'),
    url(r'^test$', views.test_view, name='test_view'),
    url(r'^ajax/autocomplete_id_producto/$', views.autocomplete_id_producto, name='autocomplete_id_producto'),
    url(r'^ajax/autocomplete_nombre_producto/$', views.autocomplete_nombre_producto, name='autocomplete_nombre_producto'),
]
urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)