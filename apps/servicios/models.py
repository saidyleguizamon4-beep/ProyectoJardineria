from django.db import models


class Servicio(models.Model):
    """Modelo de servicios"""
    
    id_servicio = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200, unique=True)
    descripcion = models.TextField()
    activo = models.BooleanField(default=True)
    duracion_estimada_minutos = models.PositiveIntegerField(default=60)
    fecha_alta = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'SERVICIOS'
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
    
    def __str__(self):
        return self.nombre


class Tarifa(models.Model):
    """Modelo de tarifas"""
    
    id_tarifa = models.AutoField(primary_key=True)
    servicio = models.ForeignKey(
        Servicio,
        on_delete=models.CASCADE,
        related_name='tarifas'
    )
    nombre_tarifa = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    duracion_minutos = models.PositiveIntegerField(default=60)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    activa = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'TARIFAS'
        verbose_name = 'Tarifa'
        verbose_name_plural = 'Tarifas'
    
    def __str__(self):
        return f"{self.servicio.nombre} - {self.nombre_tarifa}"