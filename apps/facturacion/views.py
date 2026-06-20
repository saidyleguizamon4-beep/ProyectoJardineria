# facturacion/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum
from decimal import Decimal
from apps.usuarios.views import verificar_sesion
from apps.trabajos.models import Trabajo, TrabajoServicio
from .models import Factura


# =============================================================================
# FACTURAS
# =============================================================================

@verificar_sesion
def lista_facturas(request):
    """Vista para listar facturas"""
    estado = request.GET.get('estado', '')
    
    if estado:
        facturas = Factura.objects.filter(estado_pago=estado)
    else:
        facturas = Factura.objects.all()
    
    facturas = facturas.select_related('trabajo', 'trabajo__propiedad', 'trabajo__propiedad__cliente').order_by('-fecha_emision')
    
    return render(request, 'facturacion/lista_facturas.html', {
        'facturas': facturas,
        'estado_filtro': estado
    })


@verificar_sesion
def crear_factura(request, trabajo_id):
    """Vista para crear factura desde un trabajo"""
    trabajo = get_object_or_404(Trabajo, pk=trabajo_id)
    
    # Verificar si ya tiene factura
    if hasattr(trabajo, 'factura'):
        messages.error(request, 'El trabajo ya tiene una factura')
        return redirect('facturacion:lista_facturas')
    
    # Calcular subtotal desde los servicios
    servicios = trabajo.servicios.all()
    subtotal = 0
    for s in servicios:
        subtotal += s.subtotal
    
    if request.method == 'POST':
        # Generar número de factura
        num_factura = request.POST.get('numero_factura', '').strip()
        
        if not num_factura:
            # Generar automáticamente
            ultimo = Factura.objects.order_by('-id_factura').first()
            if ultimo:
                num = int(ultimo.numero_factura.replace('FAC-', '')) + 1
            else:
                num = 1
            num_factura = f"FAC-{num:05d}"
        
        iva = Decimal(request.POST.get('iva', '21').strip())
        
        # Calcular total
        iva_monto = subtotal * (iva / Decimal('100'))
        total = subtotal + iva_monto
        
        Factura.objects.create(
            trabajo=trabajo,
            numero_factura=num_factura,
            fecha_emision=timezone.now().date(),
            subtotal=subtotal,
            iva=iva,
            total=total,
            estado_pago='pendiente'
        )
        
        # Cambiar estado del trabajo
        trabajo.estado = 'completado'
        trabajo.save()
        
        messages.success(request, f'Factura {num_factura} creada correctamente')
        return redirect('facturacion:lista_facturas')
    
    return render(request, 'facturacion/form_factura.html', {
        'trabajo': trabajo,
        'servicios': servicios,
        'subtotal': subtotal
    })


@verificar_sesion
def detalle_factura(request, pk):
    """Vista para ver detalles de factura"""
    factura = get_object_or_404(Factura.objects.select_related('trabajo', 'trabajo__propiedad', 'trabajo__propiedad__cliente'), pk=pk)
    servicios = factura.trabajo.servicios.all()
    
    return render(request, 'facturacion/detalle_factura.html', {
        'factura': factura,
        'servicios': servicios
    })


@verificar_sesion
def editar_factura(request, pk):
    """Vista para editar factura"""
    factura = get_object_or_404(Factura, pk=pk)
    
    if request.method == 'POST':
        numero_factura = request.POST.get('numero_factura', '').strip()
        fecha_emision = request.POST.get('fecha_emision', '').strip()
        iva = Decimal(request.POST.get('iva', '21').strip())
        
        # Recalcular total
        iva_monto = factura.subtotal * (iva / Decimal('100'))
        total = factura.subtotal + iva_monto
        
        if numero_factura:
            factura.numero_factura = numero_factura
        if fecha_emision:
            factura.fecha_emision = fecha_emision
        factura.iva = iva
        factura.total = total
        factura.save()
        
        messages.success(request, 'Factura actualizada correctamente')
        return redirect('facturacion:lista_facturas')
    
    return render(request, 'facturacion/form_factura.html', {
        'factura': factura,
        'solo_lectura': False
    })


@verificar_sesion
def eliminar_factura(request, pk):
    """Vista para eliminar factura"""
    factura = get_object_or_404(Factura, pk=pk)
    
    if request.method == 'POST':
        # Devolver estado del trabajo
        factura.trabajo.estado = 'completado'
        factura.trabajo.save()
        
        factura.delete()
        messages.success(request, 'Factura eliminada correctamente')
        return redirect('facturacion:lista_facturas')
    
    return render(request, 'facturacion/confirmar_eliminar.html', {
        'factura': factura
    })


@verificar_sesion
def marcar_pagada(request, pk):
    """Vista para marcar factura como pagada"""
    factura = get_object_or_404(Factura, pk=pk)
    
    if request.method == 'POST':
        factura.estado_pago = 'pagada'
        factura.save()
        
        messages.success(request, 'Factura marcada como pagada')
        return redirect('facturacion:lista_facturas')
    
    return render(request, 'facturacion/confirmar_pago.html', {
        'factura': factura
    })


