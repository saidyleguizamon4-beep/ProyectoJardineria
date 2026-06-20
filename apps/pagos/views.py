# pagos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum
from apps.usuarios.views import verificar_sesion
from apps.facturacion.models import Factura
from .models import MetodoPago, Pago


# =============================================================================
# MÉTODOS DE PAGO
# =============================================================================

@verificar_sesion
def lista_metodos_pago(request):
    """Vista para listar métodos de pago"""
    metodos = MetodoPago.objects.all().order_by('nombre')
    return render(request, 'pagos/lista_metodos_pago.html', {
        'metodos': metodos
    })


@verificar_sesion
def crear_metodo_pago(request):
    """Vista para crear método de pago"""
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        
        if not nombre:
            messages.error(request, 'El nombre es requerido')
        elif MetodoPago.objects.filter(nombre=nombre).exists():
            messages.error(request, 'El método de pago ya existe')
        else:
            MetodoPago.objects.create(
                nombre=nombre,
                descripcion=descripcion
            )
            messages.success(request, 'Método de pago creado correctamente')
            return redirect('pagos:lista_metodos_pago')
    
    return render(request, 'pagos/form_metodo_pago.html')


@verificar_sesion
def editar_metodo_pago(request, pk):
    """Vista para editar método de pago"""
    metodo = get_object_or_404(MetodoPago, pk=pk)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        activo = request.POST.get('activo', False)
        
        if not nombre:
            messages.error(request, 'El nombre es requerido')
            return render(request, 'pagos/form_metodo_pago.html', {'metodo': metodo})
        
        metodo.nombre = nombre
        metodo.descripcion = descripcion
        metodo.activo = bool(activo)
        metodo.save()
        
        messages.success(request, 'Método de pago actualizado correctamente')
        return redirect('pagos:lista_metodos_pago')
    
    return render(request, 'pagos/form_metodo_pago.html', {'metodo': metodo})


# =============================================================================
# PAGOS
# =============================================================================

@verificar_sesion
def lista_pagos(request):
    """Vista para listar pagos"""
    pagos = Pago.objects.select_related('factura', 'metodo_pago').order_by('-fecha_pago')
    
    return render(request, 'pagos/lista_pagos.html', {
        'pagos': pagos
    })


@verificar_sesion
def crear_pago(request):
    """Vista para registrar un pago"""
    facturas = Factura.objects.filter(estado_pago='pendiente')
    metodos = MetodoPago.objects.filter(activo=True)
    
    if request.method == 'POST':
        factura_id = request.POST.get('factura', '').strip()
        metodo_id = request.POST.get('metodo_pago', '').strip()
        monto = request.POST.get('monto', '').strip()
        referencia = request.POST.get('referencia', '').strip()
        
        errores = []
        
        if not factura_id:
            errores.append('La factura es requerida')
        if not metodo_id:
            errores.append('El método de pago es requerido')
        if not monto:
            errores.append('El monto es requerido')
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'pagos/form_pago.html', {
                'facturas': facturas,
                'metodos': metodos
            })
        
        try:
            factura = Factura.objects.get(id_factura=factura_id)
        except Factura.DoesNotExist:
            messages.error(request, 'La factura no existe')
            return render(request, 'pagos/form_pago.html', {
                'facturas': facturas,
                'metodos': metodos
            })
        
        try:
            metodo = MetodoPago.objects.get(id_metodo=metodo_id)
        except MetodoPago.DoesNotExist:
            messages.error(request, 'El método de pago no existe')
            return render(request, 'pagos/form_pago.html', {
                'facturas': facturas,
                'metodos': metodos
            })
        
        # Verificar monto
        if float(monto) > float(factura.total):
            messages.warning(request, 'El monto excede el total de la factura')
        
        # Crear pago
        Pago.objects.create(
            factura=factura,
            metodo_pago=metodo,
            fecha_pago=timezone.now(),
            monto=monto,
            referencia=referencia,
            estado='completado'
        )
        
        # Verificar si la factura está pagada completamente
        pagos_anteriores = Pago.objects.filter(factura=factura).aggregate(
            total=Sum('monto')
        )
        total_pagado = float(pagos_anteriores['total'] or 0) + float(monto)
        
        if total_pagado >= float(factura.total):
            factura.estado_pago = 'pagada'
            factura.save()
        
        messages.success(request, 'Pago registrado correctamente')
        return redirect('pagos:lista_pagos')
    
    return render(request, 'pagos/form_pago.html', {
        'facturas': facturas,
        'metodos': metodos
    })


@verificar_sesion
def detalle_pago(request, pk):
    """Vista para ver detalles del pago"""
    pago = get_object_or_404(Pago.objects.select_related('factura', 'metodo_pago'), pk=pk)
    
    return render(request, 'pagos/detalle_pago.html', {
        'pago': pago
    })


@verificar_sesion
def eliminar_pago(request, pk):
    """Vista para eliminar pago"""
    pago = get_object_or_404(Pago, pk=pk)
    
    if request.method == 'POST':
        # Devolver estado de la factura
        factura = pago.factura
        pagos_restantes = Pago.objects.filter(factura=factura).exclude(pk=pago.pk).aggregate(total=Sum('monto'))
        total_pagado = float(pagos_restantes['total'] or 0)
        
        if total_pagado >= float(factura.total):
            factura.estado_pago = 'pagada'
        else:
            factura.estado_pago = 'pendiente'
        factura.save()
        
        pago.delete()
        messages.success(request, 'Pago eliminado correctamente')
        return redirect('pagos:lista_pagos')
    
    return render(request, 'pagos/confirmar_eliminar.html', {
        'pago': pago
    })


# =============================================================================
# REPORTES
# =============================================================================

@verificar_sesion
def reportes_pagos(request):
    """Vista para reportes de pagos"""
    # Pagos del día
    pagos_hoy = Pago.objects.filter(
        fecha_pago__date=timezone.now().date()
    ).aggregate(total=Sum('monto'))
    
    # Pagos del mes
    pagos_mes = Pago.objects.filter(
        fecha_pago__month=timezone.now().month,
        fecha_pago__year=timezone.now().year
    ).aggregate(total=Sum('monto'))
    
    return render(request, 'pagos/reportes_pagos.html', {
        'pagos_hoy': pagos_hoy['total'] or 0,
        'pagos_mes': pagos_mes['total'] or 0
    })

