
from django.db import models
from clientes.models import Propiedad
from servicios.models import Servicio, Tarifa
from empleados.models import Empleado


class Trabajo(models.Model):
    """Modelo de trabajos operativos"""
    
    id_trabajo = models.AutoField(primary_key=True)
    propiedad = models.ForeignKey(
        Propiedad,
        on_delete=models.CASCADE,
        related_name='trabajos'
    )
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)
    num_trabajadores = models.PositiveIntegerField(default=1)
    estado = models.CharField(max_length=50)
    satisfaccion_cliente = models.PositiveIntegerField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'TRABAJO'
        verbose_name = 'Trabajo'
        verbose_name_plural = 'Trabajos'
    
    def __str__(self):
        return f"Trabajo #{self.id_trabajo}"


class TrabajoServicio(models.Model):
    """Modelo de relación trabajo-servicio"""
    
    id = models.AutoField(primary_key=True)
    trabajo = models.ForeignKey(
        Trabajo,
        on_delete=models.CASCADE,
        related_name='servicios'
    )
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE
    )
    tarifa = models.ForeignKey(
        Tarifa,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'TRABAJO_SERVICIO'
        verbose_name = 'Trabajo Servicio'
        verbose_name_plural = 'Trabajo Servicios'
    
    def __str__(self):
        return f"{self.trabajo.id} - {self.servicio.nombre}"
    
    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)


class AsignacionTrabajo(models.Model):
    """Modelo de asignación de empleados a trabajos"""
    
    id = models.AutoField(primary_key=True)
    trabajo = models.ForeignKey(
        Trabajo,
        on_delete=models.CASCADE,
        related_name='asignaciones'
    )
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name='asignaciones'
    )
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=50, default='pendiente')
    observaciones = models.TextField(blank=True)
    
    class Meta:
        db_table = 'ASIGNACION_TRABAJO'
        verbose_name = 'Asignación Trabajo'
        verbose_name_plural = 'Asignaciones Trabajo'
    
    def __str__(self):
        return f"Trabajo #{self.trabajo.id} - Empleado #{self.empleado.id}"