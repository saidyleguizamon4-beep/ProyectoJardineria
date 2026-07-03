# facturacion/urls.py
from django.urls import path
from . import views

app_name = 'facturacion'

urlpatterns = [
    # Facturas
    path('', views.lista_facturas, name='lista_facturas'),
    path('crear/', views.seleccionar_trabajo, name='seleccionar_trabajo'),
    path('crear/<int:trabajo_id>/', views.crear_factura, name='crear_factura'),
    path('<int:pk>/', views.detalle_factura, name='detalle_factura'),
    path('<int:pk>/editar/', views.editar_factura, name='editar_factura'),
    path('<int:pk>/eliminar/', views.eliminar_factura, name='eliminar_factura'),
    path('<int:pk>/marcar-pagada/', views.marcar_pagada, name='marcar_pagada'),
    path('<int:pk>/imprimir/', views.imprimir_factura, name='imprimir_factura'),
]