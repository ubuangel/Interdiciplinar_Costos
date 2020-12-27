from django.shortcuts import get_object_or_404
from .serializer import productSerliz, batchSerliz, salesSerliz, fee_progSerliz, BatchStatusSerliz, StatisticsSerliz
from .models import TarifaP, Producto, Lote, Venta, Moneda, EstadoLote, Estadisticas
from rest_framework import viewsets, status, permissions
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from . import utility

class fee_progViewSet(viewsets.ModelViewSet):
    queryset = TarifaP.objects.all()
    serializer_class = fee_progSerliz
    permission_classes = (permissions.IsAuthenticated,)


class productViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = productSerliz
    permission_classes = (permissions.IsAuthenticated,)


class batchViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Lote.objects.all()
    serializer_class = batchSerliz

class salesViewSet(viewsets.ModelViewSet):
    queryset = Venta.objects.all()
    serializer_class = salesSerliz
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = 'orden_id'

class statisticsViewset(viewsets.ModelViewSet):
    queryset = Estadisticas.objects.all()
    serializer_class = StatisticsSerliz
    permission_classes = (permissions.IsAuthenticated,)
    
class salesCustom(APIView):
    """
    Delete sales entry. This will increment the relative batch quantity and cost
    """
    def delete(self, request, orden_id):
        salesObj = get_object_or_404(Venta, orden_id=orden_id)
        batchstatus=None
        try:
            batchObj=Lote.objects.get(batch_id__exact=salesObj.lote_id)
            batchObj.cuanto=batchObj.cuanto+1
            batchObj.total_cost=batchObj.total_cost+batchObj.unidad_precio
            batchstatus=batchObj.estado
            batchObj.save()
        except:
            batchObj=Lote()
            batchObj.producto_tipo=salesObj.producto_tipo
            batchObj.cuanto=salesObj.cuanto
            batchObj.batch_id=str(salesObj.producto_tipo)+"return"
            batchObj.unidad_precio=salesObj.venta_precio-salesObj.unidad_bene
            batchObj.min_selling=utility.calcultate_min_selling(batchObj.unidad_precio,request.META["HTTP_fee_prog"])
            batchObj.moneda=Moneda.objects.get(name__exact='SAR')
            batchObj.total_costo=batchObj.unidad_precio*batchObj.cuanto
            batchObj.profit10=utility.calculate_selling_profit_percent(batchObj.unidad_precio,request.META["HTTP_fee_prog"],0.1)
            batchObj.estado=Lote.objects.get(name__exact=request.META["HTTP_STATUS"])
            batchstatus=batchObj.estado
            batchObj.save()
        utility.edit_statistics('total',-salesObj.total_bene)
        utility.edit_statistics('capital',-salesObj.venta_precio*salesObj.cuanto)
        utility.edit_statistics(batchstatus,batchObj.unidad_precio*salesObj.cuanto)
        salesObj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
