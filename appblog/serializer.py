from rest_framework import serializers
from .models import Producto,Lote,Venta,TarifaP,EstadoLote,Estadisticas
class productSerliz(serializers.ModelSerializer):
    class Meta:
        model=Producto
        fields=('nombre','descripcion','avalible')

class batchSerliz(serializers.ModelSerializer):
    class Meta:
        model=Lote
        lookup_field='lote_id'
        fields=('producto_tipo','unidad_precio','cuanto','lote_id','min_venta','total_costo','bene10','tarifa_prog','fecha','estado')

class salesSerliz(serializers.ModelSerializer):
    class Meta:
        model=Venta
        fields=('producto_tipo','cuanto','venta_precio','unidad_bene','bene_porcentaje','total_bene','fecha','orden_id','lote_id')

class fee_progSerliz(serializers.ModelSerializer):
    class Meta:
        model=TarifaP
        fields=('nombre','agre_ta','multiplicar_ta')

class BatchStatusSerliz(serializers.ModelSerializer):
    class Meta:
        model=EstadoLote
        fields=('nombre')
class StatisticsSerliz(serializers.ModelSerializer):
    class Meta:
        model=Estadisticas
        fields=('nombre','valor')
