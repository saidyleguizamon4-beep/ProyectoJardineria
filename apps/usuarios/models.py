from django.db import models

class Roles(models.Model):
    """Modelo de roles de usuario"""
    
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        db_table = 'ROLES'
    
    def __str__(self):
        return self.nombre_rol

class Usuario(models.Model):
    """Modelo de usuario del sistema"""
    
    id_usuario = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    rol = models.ForeignKey(
        Roles,
        on_delete=models.CASCADE,
        related_name='usuario')
    autenticacion = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultimo_login = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'USUARIOS'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return self.username



