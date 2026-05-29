from django.db import models


class Empleado(models.Model):
    """Modelo de empleados"""
    
    id_empleado = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='empleados',
        null=True,
        blank=True
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    dni = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=20)
    cargo = models.CharField(max_length=100)
    fecha_contratacion = models.DateField()
    activo = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True)
    fecha_alta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'EMPLEADOS'
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
