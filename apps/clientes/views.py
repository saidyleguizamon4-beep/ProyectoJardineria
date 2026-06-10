from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .models import Cliente, Propiedad
from apps.usuarios.views import verificar_sesion


# =============================================================================
# CLIENTES
# =============================================================================

@verificar_sesion
def lista_clientes(request):
    """Vista para listar clientes"""
    clientes = Cliente.objects.all().order_by('-fecha_alta')
    return render(request, 'clientes/lista_clientes.html', {
        'clientes': clientes
    })


@verificar_sesion
def crear_cliente(request):
    """Vista para crear nuevo cliente"""
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        
        # Validaciones
        errores = []
        
        if not nombre:
            errores.append('El nombre es requerido')
        if not apellido:
            errores.append('El apellido es requerido')
        if not email:
            errores.append('El email es requerido')
        if Cliente.objects.filter(email=email).exists():
            errores.append('El email ya está registrado')
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'clientes/form_cliente.html')
        
        # Crear cliente
        Cliente.objects.create(
            nombre=nombre,
            apellido=apellido,
            email=email,
            telefono=telefono,
            direccion=direccion
        )
        
        messages.success(request, 'Cliente creado correctamente')
        return redirect('clientes:lista_clientes')
    
    return render(request, 'clientes/form_cliente.html')


@verificar_sesion
def detalle_cliente(request, pk):
    """Vista para ver detalles de cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    propiedades = cliente.propiedades.all()
    return render(request, 'clientes/detalle_cliente.html', {
        'cliente': cliente,
        'propiedades': propiedades
    })


@verificar_sesion
def editar_cliente(request, pk):
    """Vista para editar cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        activo = request.POST.get('activo', False)
        
        # Validaciones
        errores = []
        
        if not nombre:
            errores.append('El nombre es requerido')
        if not email:
            errores.append('El email es requerido')
        if Cliente.objects.filter(email=email).exclude(pk=pk).exists():
            errores.append('El email ya está registrado')
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'clientes/form_cliente.html', {
                'cliente': cliente
            })
        
        # Actualizar cliente
        cliente.nombre = nombre
        cliente.apellido = apellido
        cliente.email = email
        cliente.telefono = telefono
        cliente.direccion = direccion
        cliente.activo = bool(activo)
        cliente.save()
        
        messages.success(request, 'Cliente actualizado correctamente')
        return redirect('clientes:lista_clientes')
    
    return render(request, 'clientes/form_cliente.html', {
        'cliente': cliente
    })


@verificar_sesion
def eliminar_cliente(request, pk):
    """Vista para eliminar cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        # Verificar si tiene propiedades
        if cliente.propiedades.exists():
            messages.error(request, 'No se puede eliminar el cliente porque tiene propiedades asociadas')
            return redirect('clientes:lista_clientes')
        
        cliente.delete()
        messages.success(request, 'Cliente eliminado correctamente')
        return redirect('clientes:lista_clientes')
    
    return render(request, 'clientes/confirmar_eliminar.html', {
        'cliente': cliente
    })


# =============================================================================
# PROPIEDADES
# =============================================================================

@verificar_sesion
def lista_propiedades(request):
    """Vista para listar propiedades"""
    propiedades = Propiedad.objects.select_related('cliente').all()
    return render(request, 'clientes/lista_propiedades.html', {
        'propiedades': propiedades
    })


@verificar_sesion
def crear_propiedad(request):
    """Vista para crear nueva propiedad"""
    clientes = Cliente.objects.filter(activo=True)
    
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        tipo = request.POST.get('tipo', '').strip()
        tamano = request.POST.get('tamano', '').strip()
        
        errores = []
        
        if not cliente_id:
            errores.append('El cliente es requerido')
        if not direccion:
            errores.append('La dirección es requerida')
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'clientes/form_propiedad.html', {
                'clientes': clientes
            })
        
        try:
            cliente = Cliente.objects.get(id_cliente=cliente_id)
        except Cliente.DoesNotExist:
            messages.error(request, 'El cliente no existe')
            return render(request, 'clientes/form_propiedad.html', {
                'clientes': clientes
            })
        
        # Crear propiedad
        Propiedad.objects.create(
            cliente=cliente,
            direccion=direccion,
            tipo=tipo,
            tamano=tamano if tamano else None
        )
        
        messages.success(request, 'Propiedad creada correctamente')
        return redirect('clientes:lista_propiedades')
    
    return render(request, 'clientes/form_propiedad.html', {
        'clientes': clientes
    })


