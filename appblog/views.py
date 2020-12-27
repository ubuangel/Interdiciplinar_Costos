from django.shortcuts import render
from .models import provedor, pedido, producto, Cliente

from django.shortcuts import render,redirect
from django.contrib import messages
from django.conf import settings
from django.http import Http404
from .forms import productform, batchform, salesform,calcform
from .models import Moneda,Producto,Lote,Venta,TarifaP,EstadoLote,Estadisticas
from .serializer import productSerliz,batchSerliz,salesSerliz,fee_progSerliz
from . import utility
from django.utils.translation import gettext as _
from datetime import date
import sys

# Create your views here.
def home(request):
    
    return render(request,'appblog/home.html')
def servicios(request):
    
    return render(request,'appblog/servicios.html')

def tienda(request):
    
    return render(request,'appblog/tienda.html')

def blog(request):
    
    return render(request,'appblog/blog.html')

def contacto(request):
    
    return render(request,'appblog/contacto.html')

def calculo(request):
   # num_b=pedido.objects.all().count()
    num_Pr=provedor.objects.all().count()
    # Libros disponibles (status = 'a')
  #$  num_instances_available=BookInstance.objects.filter(status__exact='a').count()
    num_p=producto.objects.count()  # El 'all()' esta implícito por defecto.
    
    # Renderiza la plantilla HTML index.html con los datos en la variable contexto
    return render(
        request,
        'appblog/calculo.html',
        context={'num_Pr':num_Pr,'num_p':num_p},
    )
    
    
    
   

def add_product(request):
    if request.method == "POST":
        form = productform(request.POST,request.FILES)
        if form.is_valid():
            proObj=Producto()
            proObj.nombre=form.cleaned_data['nombre']
            proObj.descripcion=form.cleaned_data['descripcion']
            proObj.unico_id=form.cleaned_data['unico_id']
            proObj.save()
            messages.info(request, _("Producto agregado Exitosamente!"))
        else:
            messages.error(request, "Un producto con ese nommre ya existe!")
    return render(request, 'addproduct.html', {'form': productform})

def remove_item(request):
    if request.method == "POST":
        form = salesform(request.POST)
        if form.is_valid():
            salesObj=Venta()
            salesObj.producto_tipo=form.cleaned_data['producto_tipo']
            salesObj.cuanto=form.cleaned_data['cuanto']
            if form.cleaned_data['sale_price_type']: #Ture significa que el usuario marcó la casilla de verificación por unidad
                salesObj.venta_precio=form.cleaned_data['venta_precio']*form.cleaned_data['cuanto']
            else:
                salesObj.venta_precio=form.cleaned_data['venta_precio']
            salesObj.lote_id=form.cleaned_data['lote_id']
            if(Venta.objects.filter(order_id__exact=form.cleaned_data['orden_id']).count()!=0):
                messages.error(request, _("Esta orden ya fue egistrada!"))
                return render(request, 'removeitem.html', {'form': salesform})
            salesObj.orden_id=form.cleaned_data['orden_id']
            batchObj = Lote.objects.get(batch_id__exact=salesObj.lote_id)
            if(salesObj.producto_tipo != getattr(batchObj, 'producto_tipo')):
                messages.error(request, _("El producto no está en este lote, elija el lote correcto!"))
                return render(request, 'removeitem.html', {'form': salesform})
            batchprice = getattr(batchObj, 'unidad_precio')
            batchQuant = getattr(batchObj, 'cuanto')
            if batchQuant > salesObj.cuanto:
                newquant=batchQuant-salesObj.cuanto
                Lote.objects.filter(batch_id__exact=salesObj.lote_id).update(cuanto=newquant)
                Lote.objects.filter(batch_id__exact=salesObj.lote_id).update(total_costo=getattr(batchObj, 'unidad_precio')*newquant)

            elif batchQuant == salesObj.cuanto:
                Lote.objects.filter(batch_id__exact=salesObj.batch_id).delete()
                salesObj.lote_id=None
                if not Lote.objects.filter(product_type__exact=salesObj.producto_tipo).exists():
                    Producto.objects.filter(name__exact=salesObj.producto_tipo).update(avalible=False)

            else:
                messages.error(request, _("¡El producto no se agrega o la cantidad es mayor que la disponible!"))
                return render(request, 'removeitem.html', {'form': salesform})

            if form.cleaned_data['sale_price_type']: #Ture significa que el usuario marcó la casilla de verificación por unidad
                salesObj.unidad_bene = salesObj.sale_price-batchprice
            else:
                salesObj.unidad_bene = (salesObj.venta_precio/salesObj.cuanto)-batchprice
            salesObj.bene_porcentaje = (salesObj.unidad_bene/salesObj.venta_precio)*100
            salesObj.total_bene = salesObj.unidad_bene*salesObj.cuanto
            salesObj.save()
            try:
                utility.edit_statistics('capital',salesObj.venta_precio*salesObj.cuanto)
                utility.edit_statistics(batchObj.status,-batchprice*salesObj.cuanto)
                utility.edit_statistics('total',salesObj.total_bene)
            except:
                print("Unexpected error:", sys.exc_info()[0])
            messages.info(request, _("Item removido exitosamente!"))
        else:
            for e in form.errors:
                messages.error(request, _("ERROR:")+e)
    return render(request, 'removeitem.html', {'form': salesform})

def add_item(request):
    if request.method == "POST":
        form = batchform(request.POST)
        if form.is_valid():
            batchObj=Batch()
            batchObj.producto_tipo=form.cleaned_data['producto_tipo']
            batchObj.tarifa_prog=form.cleaned_data['tarifa_prog']
            batchObj.cuanto=form.cleaned_data['cuanto']
            batchObj.moneda=form.cleaned_data['moneda']
            batchObj.unidad_precio=form.cleaned_data['total_costo']/batchObj.cuanto
            tipo_cambio = getattr(Moneda.objects.get(name__exact=batchObj.moneda), 'tipo_cambio')
            batchObj.unidad_precio *= tipo_cambio
            batchObj.total_costo=form.cleaned_data['total_costo']*tipo_cambio
            batchObj.min_selling = utility.calcultate_min_selling(batchObj.unidad_precio,batchObj.tarifa_prog)
            batchObj.profit10 = utility.calculate_selling_profit_percent(batchObj.unidad_precio,batchObj.tarifa_prog,0.1)
            batchObj.status= form.cleaned_data['estado']
            if(form.cleaned_data['batch_id']==""):
                batchObj.batch_id=str(batchObj.producto_tipo)
                batchObj.batch_id+=" Q"+str(batchObj.cuanto)+" "+str(round(batchObj.unidad_precio,2))+" "+date.today().strftime("%d %b")
            else:
                batchObj.batch_id=form.cleaned_data['lote_id']
            batchObj.save()
            Product.objects.filter(name__exact=form.cleaned_data['producto_tipo']).update(avalible=True)
            utility.edit_statistics('capital',-batchObj.total_costo)
            try:
                utility.edit_statistics(batchObj.status,batchObj.total_costo)
            except:
                utility.create_statistics(batchObj.status,batchObj.total_costo)
            messages.info(request, _("Item agregado exitosamente!"))
        else:
            for e in form.errors:
                messages.error(request, "ERROR:"+e)
    return render(request, 'additem.html', {'form': batchform})

def report_sales(request):
    return render(request, 'repsales.html')

def report_products(request):
    return render(request, 'repproducts.html')

def report_batches(request):
    return render(request, 'repbatches.html',{'batchStatus':utility.queryset_to_jslist(BatchStatus.objects.all())}) #dado que tenemos una pequeña cantidad de estados, esto no debería ser pesado en RAM
def report_statistics(request):
    return render(request, 'repstatistics.html')

def home(request):
    return render(request, 'home.html')

def login(request):
    return redirect('/accounts/login/')

def calculate_profit(request):
    if request.method=="POST":
        form=calcform(request.POST)
        if form.is_valid() :
            tarifa_prog = TarifaP.objects.get(name__exact=form.cleaned_data['tarifa_prog'])
            exchange_rate = getattr(Moneda.objects.get(name__exact=form.cleaned_data['moneda']), 'tipo_cambio')
            localprice=form.cleaned_data['local_price']
            onlineprice=float(form.cleaned_data['unidad_costo'])*tipo_cambio
            min_venta = utility.calcultate_min_selling(onlineprice,tarifa_prog)
            messages.info(request, _("Precio de venta minimo es ")+" {0:.2f} ".format(min_selling))
            messages.info(request,_("La diferencia entre venta mínima y precio local: ")+" {0:.2f} ".format(min_selling-localprice))
            messages.info(request,_("Porcentaje de beneficio a precio local: ")+" {0:.2f} % ".format(utility.calculate_profit_percent(onlineprice,tarifa_prog,localprice)))
    return render(request, 'calc.html', {'form': calcform})

def get_batches_for_product(request,product):
    if product != "null":
        batches=Lote.objects.filter(product_type__exact=product,status__in=['FBS','Stock'])
        return render(request,'batchesforproduct.html',{'batches':batches})
    return render(request,'batchesforproduct.html',{'batches':None})

def remove_sales_order(request):
    fee_progs=FeeProgram.objects.all()
    statuss=BatchStatus.objects.all()
    return render(request,'removesaleorder.html',{'fee_progs':fee_progs,'statuss':statuss})

def change_batch_status(request):
    batchObj=Batch.objects.get(batch_id__exact=request.META["HTTP_batch_id"])
    utility.edit_statistics(batchObj.status,-batchObj.total_cost)
    batchObj.status=BatchStatus.objects.get(name__exact=request.META["HTTP_NEWVAL"])
    utility.edit_statistics(batchObj.status,batchObj.total_cost)
    batchObj.save()
    return redirect('/rep/batches')

def edit_company_capital(request):
    utility.new_statistics_value('capital',float(request.META["HTTP_NEWVAL"]))
    temp={}
    totalStat=Estadisticas.objects.get(name__exact='total')
    totalStat.value=float(request.META["HTTP_NEWVAL"])
    for i in Lote.objects.values('status','total_costo'):
        temp[i['status']]=temp.get(i['status'],0)+i['total_costo']
    for i in temp:
        tStat=None
        try:
            tStat=Estadisticas.objects.get(name__exact=i)
        except:
            tStat=Estadisticas()
            tStat.name=i
        tStat.value=float(temp[i])
        totalStat.value+=tStat.value
        tStat.save()
    totalStat.save()

    return redirect('/rep/statistics/')
    
