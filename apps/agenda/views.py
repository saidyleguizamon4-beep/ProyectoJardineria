# agenda/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.utils import timezone
from apps.usuarios.views import verificar_sesion
from apps.clientes.models import Cliente
from apps.empleados.models import Empleado
from .models import AgendaCita

# =============================================================================
# CITAS
# =============================================================================

@verificar_sesion
def lista_citas(request):
    """Vista para listar citas"""
    # Filtrar por fecha si se proporciona
    fecha_filtro = request.GET.get('fecha', '')
    
    if fecha_filtro:
        citas = AgendaCita.objects.filter(fecha=fecha_filtro).select_related('cliente', 'empleado')
    else:
        citas = AgendaCita.objects.all().select_related('cliente', 'empleado')
    
    citas = citas.order_by('fecha', 'hora')
    
    return render(request, 'agenda/lista_citas.html', {
        'citas': citas,
        'fecha_filtro': fecha_filtro
    })


@verificar_sesion
def crear_cita(request):
    """Vista para crear nueva cita"""
    clientes = Cliente.objects.filter(activo=True)
    empleados = Empleado.objects.filter(activo=True)
    
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente', '').strip()
        empleado_id = request.POST.get('empleado', '').strip()
        fecha = request.POST.get('fecha', '').strip()
        hora = request.POST.get('hora', '').strip()
        motivo = request.POST.get('motivo', '').strip()
        comentarios = request.POST.get('comentarios', '').strip()
        
        errores = []
        
        if not cliente_id:
            errores.append('El cliente es requerido')
        if not fecha:
            errores.append('La fecha es requerida')
        if not hora:
            errores.append('La hora es requerida')
        if not motivo:
            errores.append('El motivo es requerido')
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'agenda/form_cita.html', {
                'clientes': clientes,
                'empleados': empleados
            })
        
        try:
            cliente = Cliente.objects.get(id_cliente=cliente_id)
        except Cliente.DoesNotExist:
            messages.error(request, 'El cliente no existe')
            return render(request, 'agenda/form_cita.html', {
                'clientes': clientes,
                'empleados': empleados
            })
        
        empleado = None
        if empleado_id:
            try:
                empleado = Empleado.objects.get(id_empleado=empleado_id)
            except Empleado.DoesNotExist:
                pass
        
        # Crear cita
        AgendaCita.objects.create(
            cliente=cliente,
            empleado=empleado,
            fecha=fecha,
            hora=hora,
            motivo=motivo,
            comentarios=comentarios,
            estado_cita='pendiente'
        )
        
        messages.success(request, 'Cita creada correctamente')
        return redirect('agenda:lista_citas')
    
    return render(request, 'agenda/form_cita.html', {
        'clientes': clientes,
        'empleados': empleados
    })


@verificar_sesion
def detalle_cita(request, pk):
    """Vista para ver detalles de cita"""
    cita = get_object_or_404(AgendaCita.objects.select_related('cliente', 'empleado'), pk=pk)
    return render(request, 'agenda/detalle_cita.html', {
        'cita': cita
    })


@verificar_sesion
def editar_cita(request, pk):
    """Vista para editar cita"""
    cita = get_object_or_404(AgendaCita, pk=pk)
    clientes = Cliente.objects.filter(activo=True)
    empleados = Empleado.objects.filter(activo=True)
    
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente', '').strip()
        empleado_id = request.POST.get('empleado', '').strip()
        fecha = request.POST.get('fecha', '').strip()
        hora = request.POST.get('hora', '').strip()
        motivo = request.POST.get('motivo', '').strip()
        comentarios = request.POST.get('comentarios', '').strip()
        estado = request.POST.get('estado_cita', '').strip()
        
        try:
            cliente = Cliente.objects.get(id_cliente=cliente_id)
        except Cliente.DoesNotExist:
            messages.error(request, 'El cliente no existe')
            return render(request, 'agenda/form_cita.html', {
                'cita': cita,
                'clientes': clientes,
                'empleados': empleados
            })
        
        empleado = None
        if empleado_id:
            try:
                empleado = Empleado.objects.get(id_empleado=empleado_id)
            except Empleado.DoesNotExist:
                pass
        
        cita.cliente = cliente
        cita.empleado = empleado
        cita.fecha = fecha
        cita.hora = hora
        cita.motivo = motivo
        cita.comentarios = comentarios
        cita.estado_cita = estado
        cita.save()
        
        messages.success(request, 'Cita actualizada correctamente')
        return redirect('agenda:lista_citas')
    
    return render(request, 'agenda/form_cita.html', {
        'cita': cita,
        'clientes': clientes,
        'empleados': empleados
    })


@verificar_sesion
def eliminar_cita(request, pk):
    """Vista para eliminar cita"""
    cita = get_object_or_404(AgendaCita, pk=pk)
    
    if request.method == 'POST':
        cita.delete()
        messages.success(request, 'Cita eliminada correctamente')
        return redirect('agenda:lista_citas')
    
    return render(request, 'agenda/confirmar_eliminar.html', {
        'cita': cita
    })


@verificar_sesion
def cambiar_estado_cita(request, pk):
    """Vista para cambiar estado de cita"""
    cita = get_object_or_404(AgendaCita, pk=pk)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado_cita', '')
        cita.estado_cita = nuevo_estado
        cita.save()
        
        messages.success(request, f'Estado cambiado a {nuevo_estado}')
        return redirect('agenda:lista_citas')
    
    return render(request, 'agenda/cambiar_estado.html', {
        'cita': cita
    })
