# usuarios/urls.py
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Usuarios
    path('', views.lista_usuarios, name='lista_usuarios'),
    path('crear/', views.crear_usuario, name='crear_usuario'),
    path('<int:pk>/', views.detalle_usuario, name='detalle_usuario'),
    path('<int:pk>/editar/', views.editar_usuario, name='editar_usuario'),
    path('<int:pk>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    path('<int:pk>/cambiar-password/', views.cambiar_password, name='cambiar_password'),
    
    # Roles
    path('roles/', views.lista_roles, name='lista_roles'),
    path('roles/crear/', views.crear_rol, name='crear_rol'),
    
    
]