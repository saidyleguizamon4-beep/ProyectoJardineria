from django.urls import path
from . import views

app_name = 'empleados'

urlpatterns = [
    path('', views.lista_empleados, name='lista_empleados'),
    path('crear/', views.crear_empleado, name='crear_empleado'),
    path('<int:pk>/', views.detalle_empleado, name='detalle_empleado'),
    path('<int:pk>/editar/', views.editar_empleado, name='editar_empleado'),
    path('<int:pk>/eliminar/', views.eliminar_empleado, name='eliminar_empleado'),
    path('validar-dni/', views.validar_dni, name='validar_dni'),
]