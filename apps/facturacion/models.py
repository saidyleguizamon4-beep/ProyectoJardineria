from django.db import models
from trabajos.models import Trabajo


class Factura(models.Model):
    """Modelo de facturas"""
    
    id_factura = models.AutoField(primary_key=True)
    trabajo = models.OneToOneField(
        Trabajo,
        on_delete=models.CASCADE,
        related_name='factura'
    )
    numero_factura = models.CharField(max_length=50, unique=True)
    fecha_emision = models.DateField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    iva = models.DecimalField(max_digits=5, decimal_places=2, default=21)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    estado_pago = models.CharField(max_length=50, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'FACTURA'
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
    
    def __str__(self):
        return f"Factura #{self.numero_factura}"
    
    def save(self, *args, **kwargs):
        if not self.subtotal:
            self.subtotal = self.trabajo.importe_total
        iva_monto = self.subtotal * (self.iva / 100)
        self.total = self.subtotal + iva_monto
        super().save(*args, **kwargs)