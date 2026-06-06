f# servicios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from usuarios.views import verificar_sesion
from .models import Servicio, Tarifa


# =============================================================================
# SERVICIOS
# =============================================================================

@verificar_sesion
def lista_servicios(request):
    """Vista para listar servicios"""
    servicios = Servicio.objects.all().order_by('nombre')
    return render(request, 'servicios/lista_servicios.html', {
        'servicios': servicios
    })


@verificar_sesion
def crear_servicio(request):
    """Vista para crear nuevo servicio"""
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        duracion = request.POST.get('duracion_estimada_minutos', '').strip()
        
        errores = []
        
        if not nombre:
            errores.append('El nombre es requerido')
        if Servicio.objects.filter(nombre=nombre).exists():
            errores.append('El servicio ya existe')
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'servicios/form_servicio.html')
        
        Servicio.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            duracion_estimada_minutos=duracion if duracion else 60
        )
        
        messages.success(request, 'Servicio creado correctamente')
        return redirect('servicios:lista_servicios')
    
    return render(request, 'servicios/form_servicio.html')


@verificar_sesion
def detalle_servicio(request, pk):
    """Vista para ver detalles del servicio"""
    servicio = get_object_or_404(Servicio, pk=pk)
    tarifas = servicio.tarifas.all()
    return render(request, 'servicios/detalle_servicio.html', {
        'servicio': servicio,
        'tarifas': tarifas
    })


@verificar_sesion
def editar_servicio(request, pk):
    """Vista para editar servicio"""
    servicio = get_object_or_404(Servicio, pk=pk)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        duracion = request.POST.get('duracion_estimada_minutos', '').strip()
        activo = request.POST.get('activo', False)
        
        if not nombre:
            messages.error(request, 'El nombre es requerido')
            return render(request, 'servicios/form_servicio.html', {
                'servicio': servicio
            })
        
        servicio.nombre = nombre
        servicio.descripcion = descripcion
        servicio.duracion_estimada_minutos = duracion if duracion else 60
        servicio.activo = bool(activo)
        servicio.save()
        
        messages.success(request, 'Servicio actualizado correctamente')
        return redirect('servicios:lista_servicios')
    
    return render(request, 'servicios/form_servicio.html', {
        'servicio': servicio
    })


@verificar_sesion
def eliminar_servicio(request, pk):
    """Vista para eliminar servicio"""
    servicio = get_object_or_404(Servicio, pk=pk)
    
    if request.method == 'POST':
        # Verificar si tiene tarifas
        if servicio.tarifas.exists():
            messages.error(request, 'No se puede eliminar el servicio porque tiene tarifas asociadas')
            return redirect('servicios:lista_servicios')
        
        servicio.delete()
        messages.success(request, 'Servicio eliminado correctamente')
        return redirect('servicios:lista_servicios')
    
    return render(request, 'servicios/confirmar_eliminar.html', {
        'servicio': servicio
    })


# =============================================================================
# TARIFAS
# =============================================================================

@verificar_sesion
def lista_tarifas(request):
    """Vista para listar tarifas"""
    tarifas = Tarifa.objects.select_related('servicio').all()
    return render(request, 'servicios/lista_tarifas.html', {
        'tarifas': tarifas
    })


@verificar_sesion
def crear_tarifa(request):
    """Vista para crear nueva tarifa"""
    servicios = Servicio.objects.filter(activo=True)
    
    if request.method == 'POST':
        servicio_id = request.POST.get('servicio', '').strip()
        nombre_tarifa = request.POST.get('nombre_tarifa', '').strip()
        precio = request.POST.get('precio', '').strip()
        duracion = request.POST.get('duracion_minutos', '').strip()
        
        errores = []
        
        if not servicio_id:
            errores.append('El servicio es requerido')
        if not nombre_tarifa:
            errores.append('El nombre de tarifa es requerido')
        if not precio:
            errores.append('El precio es requerido')
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'servicios/form_tarifa.html', {
                'servicios': servicios
            })
        
        try:
            servicio = Servicio.objects.get(id_servicio=servicio_id)
        except Servicio.DoesNotExist:
            messages.error(request, 'El servicio no existe')
            return render(request, 'servicios/form_tarifa.html', {
                'servicios': servicios
            })
        
        Tarifa.objects.create(
            servicio=servicio,
            nombre_tarifa=nombre_tarifa,
            precio=precio,
            duracion_minutos=duracion if duracion else 60
        )
        
        messages.success(request, 'Tarifa creada correctamente')
        return redirect('servicios:lista_tarifas')
    
    return render(request, 'servicios/form_tarifa.html', {
        'servicios': servicios
    })


@verificar_sesion
def editar_tarifa(request, pk):
    """Vista para editar tarifa"""
    tarifa = get_object_or_404(Tarifa, pk=pk)
    servicios = Servicio.objects.filter(activo=True)
    
    if request.method == 'POST':
        servicio_id = request.POST.get('servicio', '').strip()
        nombre_tarifa = request.POST.get('nombre_tarifa', '').strip()
        precio = request.POST.get('precio', '').strip()
        duracion = request.POST.get('duracion_minutos', '').strip()
        activa = request.POST.get('activa', False)
        
        try:
            servicio = Servicio.objects.get(id_servicio=servicio_id)
        except Servicio.DoesNotExist:
            messages.error(request, 'El servicio no existe')
            return render(request, 'servicios/form_tarifa.html', {
                'tarifa': tarifa,
                'servicios': servicios
            })
        
        tarifa.servicio = servicio
        tarifa.nombre_tarifa = nombre_tarifa
        tarifa.precio = precio
        tarifa.duracion_minutos = duracion if duracion else 60
        tarifa.activa = bool(activa)
        tarifa.save()
        
        messages.success(request, 'Tarifa actualizada correctamente')
        return redirect('servicios:lista_tarifas')
    
    return render(request, 'servicios/form_tarifa.html', {
        'tarifa': tarifa,
        'servicios': servicios
    })


@verificar_sesion
def eliminar_tarifa(request, pk):
    """Vista para eliminar tarifa"""
    tarifa = get_object_or_404(Tarifa, pk=pk)
    
    if request.method == 'POST':
        tarifa.delete()
        messages.success(request, 'Tarifa eliminada correctamente')
        return redirect('servicios:lista_tarifas')
    
    return render(request, 'servicios/confirmar_eliminar_tarifa.html', {
        'tarifa': tarifa
    })