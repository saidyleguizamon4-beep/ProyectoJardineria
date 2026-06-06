# empleados/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from usuarios.views import verificar_sesion
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
        dni = request.POST.get('dni', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        cargo = request.POST.get('cargo', '').strip()
        fecha_contratacion = request.POST.get('fecha_contratacion', '').strip()
        
        # Validaciones
        errores = []
        
        if not nombre:
            errores.append('El nombre es requerido')
        if not apellido:
            errores.append('El apellido es requerido')
        if not dni:
            errores.append('El DNI es requerido')
        if Empleado.objects.filter(dni=dni).exists():
            errores.append('El DNI ya está registrado')
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'empleados/form_empleado.html')
        
        # Crear empleado
        Empleado.objects.create(
            nombre=nombre,
            apellido=apellido,
            dni=dni,
            email=email,
            telefono=telefono,
            cargo=cargo,
            fecha_contratacion=fecha_contratacion if fecha_contratacion else None
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

