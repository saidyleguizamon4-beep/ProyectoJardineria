from django.db import models

class Cliente(models.Model):
    """Modelo de clientes"""
    
    id_cliente = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        related_name='clientes',
        null=True,
        blank=True
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20)
    direccion = models.CharField(max_length=300)
    fecha_alta = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'CLIENTES'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"
class Propiedad(models.Model):
    """Modelo de propiedades"""
    
    id_propiedad = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='propiedades'
    )
    direccion = models.CharField(max_length=300)
    tipo = models.CharField(max_length=50)
    tamano = models.DecimalField(max_digits=10, decimal_places=2)
    numero_habitaciones = models.PositiveIntegerField(default=1)
    numero_banos = models.PositiveIntegerField(default=1)
    tiene_piscina = models.BooleanField(default=False)
    tiene_jardin = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True)
    fecha_alta = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'PROPIEDAD'
        verbose_name = 'Propiedad'
        verbose_name_plural = 'Propiedades'
    
    def __str__(self):
        return f"{self.direccion} - {self.cliente.nombre}"