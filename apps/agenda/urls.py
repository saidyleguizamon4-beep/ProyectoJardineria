# agenda/urls.py
from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    # Citas
    path('', views.lista_citas, name='lista_citas'),
    path('crear/', views.crear_cita, name='crear_cita'),
    path('<int:pk>/', views.detalle_cita, name='detalle_cita'),
    path('<int:pk>/editar/', views.editar_cita, name='editar_cita'),
    path('<int:pk>/eliminar/', views.eliminar_cita, name='eliminar_cita'),
    path('<int:pk>/cambiar-estado/', views.cambiar_estado_cita, name='cambiar_estado'),
    
]