# pagos/urls.py
from django.urls import path
from . import views

app_name = 'pagos'

urlpatterns = [
    # Métodos de pago
    path('metodos/', views.lista_metodos_pago, name='lista_metodos_pago'),
    path('metodos/crear/', views.crear_metodo_pago, name='crear_metodo_pago'),
    path('metodos/<int:pk>/editar/', views.editar_metodo_pago, name='editar_metodo_pago'),
    
    # Pagos
    path('', views.lista_pagos, name='lista_pagos'),
    path('crear/', views.crear_pago, name='crear_pago'),
    path('<int:pk>/', views.detalle_pago, name='detalle_pago'),
    path('<int:pk>/eliminar/', views.eliminar_pago, name='eliminar_pago'),
    
    # Reportes
    path('reportes/', views.reportes_pagos, name='reportes_pagos'),
    

]