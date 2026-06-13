# clientes/urls.py
from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # Clientes
    path('', views.lista_clientes, name='lista_clientes'),
    path('crear/', views.crear_cliente, name='crear_cliente'),
    path('<int:pk>/', views.detalle_cliente, name='detalle_cliente'),
    path('<int:pk>/editar/', views.editar_cliente, name='editar_cliente'),
    path('<int:pk>/eliminar/', views.eliminar_cliente, name='eliminar_cliente'),
    
    # Propiedades
    path('propiedades/', views.lista_propiedades, name='lista_propiedades'),
    path('propiedades/crear/', views.crear_propiedad, name='crear_propiedad'),
    path('propiedades/<int:pk>/', views.detalle_propiedad, name='detalle_propiedad'),
    path('propiedades/<int:pk>/editar/', views.editar_propiedad, name='editar_propiedad'),
    path('propiedades/<int:pk>/eliminar/', views.eliminar_propiedad, name='eliminar_propiedad'),
]