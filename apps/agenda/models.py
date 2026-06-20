from django.db import models
from apps.clientes.models import Cliente
from apps.empleados.models import Empleado
from apps.trabajos.models import Trabajo


class AgendaCita(models.Model):
    """Modelo de citas programadas"""
    
    id_cita = models.AutoField(primary_key=True)
    trabajo = models.ForeignKey(
        Trabajo,
        on_delete=models.CASCADE,
        related_name='citas')
    
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='citas'
    )
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='citas'
    )
    fecha = models.DateField()
    hora = models.TimeField()
    estado_cita = models.CharField(max_length=50)
    comentarios = models.TextField(blank=True)
    recordatorios = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'AGENDA_CITAS'
        verbose_name = 'Cita'
        verbose_name_plural = 'Citas'
        ordering = ['-fecha', '-hora']
    
    def __str__(self):
        return f"Cita #{self.id_cita} - {self.fecha} {self.hora}"