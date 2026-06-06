# servicios/urls.py
from django.urls import path
from . import views

app_name = 'servicios'

urlpatterns = [
    # Servicios
    path('', views.lista_servicios, name='lista_servicios'),
    path('crear/', views.crear_servicio, name='crear_servicio'),
    path('<int:pk>/', views.detalle_servicio, name='detalle_servicio'),
    path('<int:pk>/editar/', views.editar_servicio, name='editar_servicio'),
    path('<int:pk>/eliminar/', views.eliminar_servicio, name='eliminar_servicio'),
    
    # Tarifas
    path('tarifas/', views.lista_tarifas, name='lista_tarifas'),
    path('tarifas/crear/', views.crear_tarifa, name='crear_tarifa'),
    path('tarifas/<int:pk>/editar/', views.editar_tarifa, name='editar_tarifa'),
    path('tarifas/<int:pk>/eliminar/', views.eliminar_tarifa, name='eliminar_tarifa'),
]