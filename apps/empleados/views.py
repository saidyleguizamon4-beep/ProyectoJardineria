# empleados/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from apps.usuarios.views import verificar_sesion
from .models import Empleado


@verificar_sesion
def lista_empleados(request):
    """Vista para listar empleados"""
    empleados = Empleado.objects.all().order_by('-fecha_alta')
    return render(request, 'empleados/lista_empleados.html', {
        'empleados': empleados
    })


@verificar_sesion
def crear_empleado(request):
    """Vista para crear nuevo empleado"""
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        documento = request.POST.get('documento', '').strip()  # ← Cambiado de dni
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        cargo = request.POST.get('cargo', '').strip()
        fecha_contratacion = request.POST.get('fecha_contratacion', '').strip()
        observaciones = request.POST.get('observaciones', '').strip()
        
        # Validaciones
        errores = []
        
        if not nombre:
            errores.append('El nombre es requerido')
        if not apellido:
            errores.append('El apellido es requerido')
        if not documento:
            errores.append('El documento es requerido')
        if Empleado.objects.filter(documento=documento).exists():  # ← Cambiado
            errores.append('El documento ya está registrado')
        if not email:
            errores.append('El email es requerido')
        if not cargo:
            errores.append('El cargo es requerido')
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'empleados/form_empleado.html')
        
        # Crear empleado
        Empleado.objects.create(
            nombre=nombre,
            apellido=apellido,
            documento=documento,  # ← Cambiado
            email=email,
            telefono=telefono,
            cargo=cargo,
            fecha_contratacion=fecha_contratacion if fecha_contratacion else None,
            observaciones=observaciones
        )
        
        messages.success(request, 'Empleado creado correctamente')
        return redirect('empleados:lista_empleados')
    
    return render(request, 'empleados/form_empleado.html')


@verificar_sesion
def detalle_empleado(request, pk):
    """Vista para ver detalles de empleado"""
    empleado = get_object_or_404(Empleado, pk=pk)
    return render(request, 'empleados/detalle_empleado.html', {
        'empleado': empleado
    })


@verificar_sesion
def editar_empleado(request, pk):
    """Vista para editar empleado"""
    empleado = get_object_or_404(Empleado, pk=pk)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        cargo = request.POST.get('cargo', '').strip()
        fecha_contratacion = request.POST.get('fecha_contratacion', '').strip()
        observaciones = request.POST.get('observaciones', '').strip()
        activo = request.POST.get('activo', False)
        
        if not nombre:
            messages.error(request, 'El nombre es requerido')
            return render(request, 'empleados/form_empleado.html', {
                'empleado': empleado
            })
        
        # Actualizar empleado
        empleado.nombre = nombre
        empleado.apellido = apellido
        empleado.email = email
        empleado.telefono = telefono
        empleado.cargo = cargo
        empleado.fecha_contratacion = fecha_contratacion
        empleado.observaciones = observaciones
        empleado.activo = bool(activo)
        empleado.save()
        
        messages.success(request, 'Empleado actualizado correctamente')
        return redirect('empleados:lista_empleados')
    
    return render(request, 'empleados/form_empleado.html', {
        'empleado': empleado
    })


@verificar_sesion
def eliminar_empleado(request, pk):
    """Vista para eliminar empleado"""
    empleado = get_object_or_404(Empleado, pk=pk)
    
    if request.method == 'POST':
        empleado.delete()
        messages.success(request, 'Empleado eliminado correctamente')
        return redirect('empleados:lista_empleados')
    
    return render(request, 'empleados/confirmar_eliminar.html', {
        'empleado': empleado
    })


@require_http_methods(["POST"])
def validar_documento(request):  # ← Cambiado de validar_dni
    """API para validar documento"""
    documento = request.POST.get('documento', '').strip()
    existe = Empleado.objects.filter(documento=documento).exists()  # ← Cambiado
    
    return JsonResponse({
        'existe': existe,
        'mensaje': 'El documento ya está registrado' if existe else 'Documento disponible'
    })