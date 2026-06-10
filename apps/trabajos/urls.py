# trabajos/urls.py
from django.urls import path
from . import views

app_name = 'trabajos'

urlpatterns = [
    # Trabajos
    path('', views.lista_trabajos, name='lista_trabajos'),
    path('crear/', views.crear_trabajo, name='crear_trabajo'),
    path('<int:pk>/', views.detalle_trabajo, name='detalle_trabajo'),
    path('<int:pk>/editar/', views.editar_trabajo, name='editar_trabajo'),
    path('<int:pk>/eliminar/', views.eliminar_trabajo, name='eliminar_trabajo'),
    
    # Servicios del trabajo
    path('<int:pk>/agregar-servicio/', views.agregar_servicio_trabajo, name='agregar_servicio'),
    
    # Asignaciones
    path('<int:pk>/asignar-empleado/', views.asignar_empleado, name='asignar_empleado'),
    path('asignacion/<int:pk>/completar/', views.completar_asignacion, name='completar_asignacion'),
    
    
]