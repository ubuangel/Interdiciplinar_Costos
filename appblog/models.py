

from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.conf import settings

# Create your models here.
class provedor(models.Model):
    nombre = models.CharField(max_length=50)
    telefono = models.CharField(max_length=9)
    direccion = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre
       

class pedido(models.Model):
        
    
    nombre = models.CharField(max_length=50)
    id_cliente = models.ForeignKey('Cliente', on_delete=models.SET_NULL, null=True)
    fecha = models.DateField(null=True, blank=True)

    cantidad = models.IntegerField()
    valortotal = models.FloatField()
    id_provedor = models.ForeignKey('provedor', on_delete=models.SET_NULL, null=True)
    valor_ival = models.FloatField()
    valor_neto = models.FloatField()
    
    LOAN_STATUS = (
        ('m', 'proceso'),
        ('o', 'no entregado'),
        ('a', 'entregado'),
        ('r', 'Reserved'),
    )
    estado = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='m', help_text='Disponibilidad del libro')
    
    def get_absolute_url(self):
        """
        Retorna la url para acceder a una instancia particular de un autor.
        """
        return reverse('pedido-detalle', args=[str(self.id)])
    

    def __str__(self):
        """
        String que representa al objeto Book
        """
        return self.nombre

   
    
class producto(models.Model):
     nombre = models.CharField(max_length=50)
     pedido = models.ManyToManyField(pedido, help_text="Seleccione un pedido")
     precio = models.FloatField()
     descripcion = models.TextField(max_length=1000, help_text="Ingrese una breve descripción del producto")
     
 
     
    
    
class Cliente(models.Model):
    nombre = models.CharField(max_length=50)
    direccion = models.CharField(max_length=50)
    telefono_cliente = models.CharField(max_length=40)
    ciudad = models.CharField(max_length=80)
    email = models.CharField(max_length=80)
    
    
class Moneda(models.Model):
    nombre=models.CharField(max_length=100,default='USD',unique=True)
    tipo_cambio=models.FloatField(blank=False,null=False,default=3.75)
    def __str__(self):
        return self.nombre
class TarifaP(models.Model):
    nombre=models.CharField(max_length=100,default='',null=False,unique=True, blank=False)
    agre_ta=models.FloatField(default=0)
    multiplicar_ta=models.FloatField(default=1)
    def __str__(self):
        return self.nombre
    class Meta:
        ordering=['nombre']        
class EstadoLote(models.Model):
    nombre=models.CharField(max_length=100,default='',null=False,unique=True, blank=False)
    costo=models.FloatField(default=0)
    def __str__(self):
        return self.nombre
class Producto(models.Model):
    unico_id=models.CharField(max_length=100,default='',null=False,unique=True, blank=False)
    nombre=models.CharField(max_length=100,default='',null=False,unique=True, blank=False)
    producto_tipo=models.CharField(max_length=100,default='',null=True,unique=False, blank=True)
    descripcion=models.CharField(max_length=1000,default='',blank=True,null=True)
    avalible=models.BooleanField(default=False)
    def __str__(self):
        return self.nombre
    class Meta:
        ordering=['nombre']
class Lote(models.Model):
    producto_tipo=models.ForeignKey(Producto,on_delete=models.SET_DEFAULT,default='')
    cuanto=models.IntegerField(default=0)
    moneda=models.ForeignKey(Moneda,on_delete=models.SET_DEFAULT,default=1)
    unidad_precio=models.FloatField(default=0.0)
    lote_id=models.CharField(max_length=100,default='',null=False,blank=False,unique=True)
    min_venta=models.FloatField(default=0)
    fecha=models.DateField(auto_now=True)
    total_costo=models.FloatField(default=0.0)
    bene10=models.FloatField(default=0.0)
    tarifa_prog=models.ForeignKey(TarifaP,on_delete=models.SET_NULL,null=True)
    fecha=models.DateField(auto_now=True)
    estado=models.ForeignKey(EstadoLote,on_delete=models.SET_DEFAULT,default='')
    def __str__(self):
       return self.lote_id
    class Meta:
        ordering=['cuanto']

class Venta(models.Model):
    producto_tipo=models.ForeignKey(Producto,on_delete=models.SET_NULL,null=True,default='')
    cuanto=models.IntegerField()
    venta_precio=models.FloatField()
    lote_id=models.ForeignKey(Lote,on_delete = models.SET_NULL, null=True, blank=True,limit_choices_to=Q(quant__gt=0))
    unidad_bene=models.FloatField(default=0.0)
    bene_porcentaje=models.FloatField(default=0.0)
    total_bene=models.FloatField(default=0.0)
    bene=models.FloatField(default=0.0)
    fecha=models.DateField(auto_now=True)
    orden_id=models.CharField(max_length=200,default='',blank=True,null=True,unique=True)
    class Meta:
        ordering=['-fecha']
class Estadisticas(models.Model):
    nombre=models.CharField(max_length=100,default='',null=False,unique=True, blank=False)
    valor=models.FloatField(default=0)
    def __str__(self):
        return self.nombre
    class Meta:
        ordering=['-nombre']
    
