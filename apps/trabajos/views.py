# trabajos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from apps.clientes.models import Propiedad
from apps.empleados.models import Empleado
from apps.servicios.models import Servicio, Tarifa
from .models import Trabajo, TrabajoServicio, AsignacionTrabajo
from apps.usuarios.views import verificar_sesion


# =============================================================================
# TRABAJOS
# =============================================================================

@verificar_sesion
def lista_trabajos(request):
    """Vista para listar trabajos"""
    estado = request.GET.get('estado', '')
    
    if estado:
        trabajos = Trabajo.objects.filter(estado=estado)
    else:
        trabajos = Trabajo.objects.all()
    
    trabajos = trabajos.select_related('propiedad', 'propiedad__cliente').order_by('-fecha_inicio')
    
    return render(request, 'trabajos/lista_trabajos.html', {
        'trabajos': trabajos,
        'estado_filtro': estado
    })


@verificar_sesion
def crear_trabajo(request):
    """Vista para crear nuevo trabajo"""
    propiedades = Propiedad.objects.all()
    empleados = Empleado.objects.filter(activo=True)
    
    if request.method == 'POST':
        propiedad_id = request.POST.get('propiedad', '').strip()
        fecha_inicio = request.POST.get('fecha_inicio', '').strip()
        num_trabajadores = request.POST.get('num_trabajadores', '1').strip()
        observaciones = request.POST.get('observaciones', '').strip()
        
        errores = []
        
        if not propiedad_id:
            errores.append('La propiedad es requerida')
        if not fecha_inicio:
            errores.append('La fecha es requerida')
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'trabajos/form_trabajo.html', {
                'propiedades': propiedades,
                'empleados': empleados
            })
        
        try:
            propiedad = Propiedad.objects.get(id_propiedad=propiedad_id)
        except Propiedad.DoesNotExist:
            messages.error(request, 'La propiedad no existe')
            return render(request, 'trabajos/form_trabajo.html', {
                'propiedades': propiedades,
                'empleados': empleados
            })
        
        # Crear trabajo
        trabajo = Trabajo.objects.create(
            propiedad=propiedad,
            fecha_inicio=fecha_inicio,
            num_trabajadores=num_trabajadores,
            observaciones=observaciones,
            estado='pendiente'
        )
        
        messages.success(request, 'Trabajo creado correctamente')
        return redirect('trabajos:lista_trabajos')
    
    return render(request, 'trabajos/form_trabajo.html', {
        'propiedades': propiedades,
        'empleados': empleados
    })


@verificar_sesion
def detalle_trabajo(request, pk):
    """Vista para ver detalles del trabajo"""
    trabajo = get_object_or_404(Trabajo.objects.select_related('propiedad', 'propiedad__cliente'), pk=pk)
    servicios = trabajo.servicios.all()
    asignaciones = trabajo.asignaciones.select_related('empleado')
    
    return render(request, 'trabajos/detalle_trabajo.html', {
        'trabajo': trabajo,
        'servicios': servicios,
        'asignaciones': asignaciones
    })


@verificar_sesion
def editar_trabajo(request, pk):
    """Vista para editar trabajo"""
    trabajo = get_object_or_404(Trabajo, pk=pk)
    propiedades = Propiedad.objects.all()
    
    if request.method == 'POST':
        propiedad_id = request.POST.get('propiedad', '').strip()
        fecha_inicio = request.POST.get('fecha_inicio', '').strip()
        fecha_fin = request.POST.get('fecha_fin', '').strip()
        num_trabajadores = request.POST.get('num_trabajadores', '1').strip()
        estado = request.POST.get('estado', '').strip()
        observaciones = request.POST.get('observaciones', '').strip()
        
        try:
            propiedad = Propiedad.objects.get(id_propiedad=propiedad_id)
        except Propiedad.DoesNotExist:
            messages.error(request, 'La propiedad no existe')
            return render(request, 'trabajos/form_trabajo.html', {
                'trabajo': trabajo,
                'propiedades': propiedades
            })
        
        trabajo.propiedad = propiedad
        trabajo.fecha_inicio = fecha_inicio
        trabajo.fecha_fin = fecha_fin if fecha_fin else None
        trabajo.num_trabajadores = num_trabajadores
        trabajo.estado = estado
        trabajo.observaciones = observaciones
        trabajo.save()
        
        messages.success(request, 'Trabajo actualizado correctamente')
        return redirect('trabajos:lista_trabajos')
    
    return render(request, 'trabajos/form_trabajo.html', {
        'trabajo': trabajo,
        'propiedades': propiedades
    })


@verificar_sesion
def eliminar_trabajo(request, pk):
    """Vista para eliminar trabajo"""
    trabajo = get_object_or_404(Trabajo, pk=pk)
    
    if request.method == 'POST':
        trabajo.delete()
        messages.success(request, 'Trabajo eliminado correctamente')
        return redirect('trabajos:lista_trabajos')
    
    return render(request, 'trabajos/confirmar_eliminar.html', {
        'trabajo': trabajo
    })


# =============================================================================
# SERVICIOS DEL TRABAJO
# =============================================================================

@verificar_sesion
def agregar_servicio_trabajo(request, pk):
    """Vista para agregar servicio a un trabajo"""
    trabajo = get_object_or_404(Trabajo, pk=pk)
    servicios = Servicio.objects.filter(activo=True)
    
    if request.method == 'POST':
        servicio_id = request.POST.get('servicio', '').strip()
        cantidad = int(request.POST.get('cantidad', '1').strip() or 1)
        
        try:
            servicio = Servicio.objects.get(id_servicio=servicio_id)
        except Servicio.DoesNotExist:
            messages.error(request, 'El servicio no existe')
            return render(request, 'trabajos/agregar_servicio.html', {
                'trabajo': trabajo,
                'servicios': servicios
            })
        
        # Obtener precio de la tarifa
        precio = 0
        tarifa = servicio.tarifas.first()
        if tarifa:
            precio = tarifa.precio
        
        TrabajoServicio.objects.create(
            trabajo=trabajo,
            servicio=servicio,
            cantidad=cantidad,
            precio_unitario=precio,
            subtotal=precio * cantidad
        )
        
        messages.success(request, 'Servicio agregado correctamente')
        return redirect('trabajos:detalle_trabajo', pk=pk)
    
    return render(request, 'trabajos/agregar_servicio.html', {
        'trabajo': trabajo,
        'servicios': servicios
    })


# =============================================================================
# ASIGNACIONES
# =============================================================================

@verificar_sesion
def asignar_empleado(request, pk):
    """Vista para asignar empleado a un trabajo"""
    trabajo = get_object_or_404(Trabajo, pk=pk)
    empleados = Empleado.objects.filter(activo=True)
    
    if request.method == 'POST':
        empleado_id = request.POST.get('empleado', '').strip()
        
        try:
            empleado = Empleado.objects.get(id_empleado=empleado_id)
        except Empleado.DoesNotExist:
            messages.error(request, 'El empleado no existe')
            return render(request, 'trabajos/asignar_empleado.html', {
                'trabajo': trabajo,
                'empleados': empleados
            })
        
        # Verificar si ya está asignado
        if AsignacionTrabajo.objects.filter(trabajo=trabajo, empleado=empleado).exists():
            messages.error(request, 'El empleado ya está asignado a este trabajo')
            return render(request, 'trabajos/asignar_empleado.html', {
                'trabajo': trabajo,
                'empleados': empleados
            })
        
        AsignacionTrabajo.objects.create(
            trabajo=trabajo,
            empleado=empleado,
            estado='pendiente'
        )
        
        # Cambiar estado del trabajo
        trabajo.estado = 'asignado'
        trabajo.save()
        
        messages.success(request, 'Empleado asignado correctamente')
        return redirect('trabajos:detalle_trabajo', pk=pk)
    
    return render(request, 'trabajos/asignar_empleado.html', {
        'trabajo': trabajo,
        'empleados': empleados
    })


@verificar_sesion
def completar_asignacion(request, pk):
    """Vista para completar una asignación"""
    asignacion = get_object_or_404(AsignacionTrabajo, pk=pk)
    
    if request.method == 'POST':
        horas = request.POST.get('horas_asignadas', '1').strip()
        
        asignacion.hora_fin = timezone.now()
        asignacion.estado = 'completada'
        asignacion.save()
        
        messages.success(request, 'Trabajo marcado como completado')
        return redirect('trabajos:detalle_trabajo', pk=asignacion.trabajo_id)
    
    return render(request, 'trabajos/completar_asignacion.html', {
        'asignacion': asignacion
    })
