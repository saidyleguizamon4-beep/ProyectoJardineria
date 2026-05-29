from django.db import models
from apps.facturacion.models import Factura


class MetodoPago(models.Model):
    """Modelo de métodos de pago"""
    
    id_metodo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'METODO_PAGO'
        verbose_name = 'Método Pago'
        verbose_name_plural = 'Métodos Pago'
    
    def __str__(self):
        return self.nombre


class Pago(models.Model):
    """Modelo de pagos"""
    
    id_pago = models.AutoField(primary_key=True)
    factura = models.ForeignKey(
        Factura,
        on_delete=models.CASCADE,
        related_name='pagos'
    )
    metodo_pago = models.ForeignKey(
        MetodoPago,
        on_delete=models.CASCADE
    )
    fecha_pago = models.DateTimeField()
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    referencia = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=50, default='completado')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'PAGOS'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
    
    def __str__(self):
        return f"Pago #{self.id_pago} - {self.monto}"