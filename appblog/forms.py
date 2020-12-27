from django import forms
from .models import Producto, Venta, Lote, Moneda,TarifaP,EstadoLote
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy


class productform(forms.Form):
    nombre = forms.CharField(label=gettext_lazy("Nombre"))
    descripcion = forms.CharField(label=gettext_lazy("Descripcion"),required=False)
    unico_id = forms.CharField(label=gettext_lazy("Identificador ID"),required=True,help_text=gettext_lazy('ASIN or SKU'))
    def is_valid(self):
        if not super().is_valid():
            return  False
        if Producto.objects.filter(name__exact=self.cleaned_data['nombre']).exists():
            return False
        if Product.objects.filter(unique_id__exact=self.cleaned_data['unico_id']).exists():
            return False
        return True
class batchform(forms.Form):
    producto_tipo = forms.ModelChoiceField(queryset=Producto.objects.all(), empty_label=None,label=gettext_lazy("Producto"))
    cuanto = forms.IntegerField(validators=[MinValueValidator(1)],label=gettext_lazy("Cantidad"))
    moneda = forms.ModelChoiceField(queryset=Moneda.objects.all(), empty_label=None,label=gettext_lazy("Moneda"),help_text=gettext_lazy('usado para comprar el producto'))
    total_cost = forms.FloatField(validators=[MinValueValidator(1)],label=gettext_lazy("Costo total de la orden"),help_text=gettext_lazy('En la moneda elegida'))
    lote_id = forms.CharField(label=gettext_lazy("Identificador de lote"),help_text=gettext_lazy('Identificador Unico para el lote de productos'),required=False)
    tarifa_prog=forms.ModelChoiceField(queryset=TarifaP.objects.all(), empty_label=None,label=gettext_lazy("Tarifa Programa"))
    estado=forms.ModelChoiceField(queryset=EstadoLote.objects.all(), empty_label=None,label=gettext_lazy("Estado"))
    
    def is_valid(self):
        if not super().is_valid():
            return  False
        if Lote.objects.filter(batch_id__exact=self.cleaned_data['lote_id']).exists():
            return False
        return True
        
class salesform(forms.Form):
    producto_tipo = forms.ModelChoiceField(queryset=Producto.objects.filter(avalible__exact=True), empty_label=None,label=gettext_lazy("Producto"))
    cuanto=forms.IntegerField(validators=[MinValueValidator(1)],label=gettext_lazy("Cantidad"),initial=1)
    venta_precio=forms.FloatField(validators=[MinValueValidator(0)],label=gettext_lazy("Ingresos"))
    sale_price_type=forms.BooleanField(required=False,label=gettext_lazy("Per unit"),help_text=gettext_lazy('Verificar que los ingresos son por unidad'))
    lote_id=forms.ModelChoiceField(queryset=Lote.objects.filter(quant__gt=0), empty_label=None,label=gettext_lazy("Lote Identificador"))
    orden_id=forms.CharField(label=gettext_lazy(" IDENTIFICADOR PARA LA ORDEN"),help_text=gettext_lazy('Unico ID para orden'))


class calcform(forms.Form):
    tarifa_prog = forms.ModelChoiceField(queryset=TarifaP.objects.all(), empty_label=None,label=gettext_lazy("Tarifa Programa"))
    moneda = forms.ModelChoiceField(queryset=Moneda.objects.all(), empty_label=None,label=gettext_lazy("Moneda"),help_text=gettext_lazy('Usado para comprar el producto'))
    unit_cost = forms.FloatField(validators=[MinValueValidator(1)],label=gettext_lazy("Costo Unitario"),help_text=gettext_lazy('En la moneda Elegida'))
    local_price=forms.FloatField(validators=[MinValueValidator(0)],label=gettext_lazy("Costo unitario en el mercado local"))
