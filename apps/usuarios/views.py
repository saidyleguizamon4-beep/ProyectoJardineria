# usuarios/views.py
# usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import hashlib
from .models import Usuario, Roles


# =============================================================================
# AUTENTICACIÓN
# =============================================================================

def login_view(request):
    """Vista para iniciar sesión"""
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not username or not password:
            messages.error(request, 'Por favor ingrese usuario y contraseña')
            return render(request, 'usuarios/login.html')
        
        # Buscar usuario
        try:
            usuario = Usuario.objects.get(username=username)
        except Usuario.DoesNotExist:
            messages.error(request, 'Usuario o contraseña incorrectos')
            return render(request, 'usuarios/login.html')
        
        # Verificar si está activo
        if not usuario.autenticacion:
            messages.error(request, 'Usuario no autorizado para iniciar sesión')
            return render(request, 'usuarios/login.html')
        
        # Verificar contraseña (comparación simple)
        if password != usuario.password:
            messages.error(request, 'Usuario o contraseña incorrectos')
            return render(request, 'usuarios/login.html')
        
        # Crear sesión
        request.session['usuario_id'] = usuario.id_usuario
        request.session['username'] = usuario.username
        request.session['rol'] = usuario.rol.nombre_rol if usuario.rol else ''
        request.session['logged_in'] = True
        
        # Actualizar último login
        usuario.ultimo_login = timezone.now()
        usuario.save(update_fields=['ultimo_login'])
        
        messages.success(request, f'Bienvenido {usuario.username}')
        return redirect('inicio')
    
    return render(request, 'usuarios/login.html')


def logout_view(request):
    """Vista para cerrar sesión"""
    request.session.flush()
    messages.success(request, 'Sesión cerrada correctamente')
    return redirect('usuarios:login')


# =============================================================================
# DECORADOR PARA VERIFICAR SESIÓN
# =============================================================================

def verificar_sesion(view_func):
    """Decorador para verificar si hay sesión activa"""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('logged_in'):
            messages.error(request, 'Debe iniciar sesión')
            return redirect('usuarios:login')
        return view_func(request, *args, **kwargs)
    return wrapper


# =============================================================================
# GESTIÓN DE USUARIOS
# =============================================================================

@verificar_sesion
def lista_usuarios(request):
    """Vista para listar usuarios"""
    usuarios = Usuario.objects.select_related('rol').all().order_by('-fecha_registro')
    return render(request, 'usuarios/lista_usuarios.html', {
        'usuarios': usuarios
    })


@verificar_sesion
def crear_usuario(request):
    """Vista para crear nuevo usuario"""
    roles = Roles.objects.all()
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        rol_id = request.POST.get('rol', '').strip()
        autenticacion = request.POST.get('autenticacion', False)
        
        # Validaciones
        errores = []
        
        if not username:
            errores.append('El usuario es requerido')
        if Usuario.objects.filter(username=username).exists():
            errores.append('El nombre de usuario ya existe')
        if not password:
            errores.append('La contraseña es requerida')
        if len(password) < 6:
            errores.append('La contraseña debe tener al menos 6 caracteres')
        if password != password_confirm:
            errores.append('Las contraseñas no coinciden')
        if not rol_id:
            errores.append('El rol es requerido')
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'usuarios/form_usuario.html', {
                'roles': roles
            })
        
        # Buscar rol
        try:
            rol = Roles.objects.get(id_rol=rol_id)
        except Roles.DoesNotExist:
            messages.error(request, 'El rol seleccionado no existe')
            return render(request, 'usuarios/form_usuario.html', {
                'roles': roles
            })
        
        # Crear usuario
        Usuario.objects.create(
            username=username,
            password=password,
            rol=rol,
            autenticacion=bool(autenticacion)
        )
        
        messages.success(request, 'Usuario creado correctamente')
        return redirect('usuarios:lista_usuarios')
    
    return render(request, 'usuarios/form_usuario.html', {
        'roles': roles
    })


@verificar_sesion
def detalle_usuario(request, pk):
    """Vista para ver detalles de usuario"""
    usuario = get_object_or_404(Usuario.objects.select_related('rol'), pk=pk)
    return render(request, 'usuarios/detalle_usuario.html', {
        'usuario': usuario
    })


@verificar_sesion
def editar_usuario(request, pk):
    """Vista para editar usuario"""
    usuario = get_object_or_404(Usuario, pk=pk)
    roles = Roles.objects.all()
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        rol_id = request.POST.get('rol', '').strip()
        autenticacion = request.POST.get('autenticacion', False)
        
        # Validaciones
        errores = []
        
        if not username:
            errores.append('El usuario es requerido')
        if Usuario.objects.filter(username=username).exclude(pk=pk).exists():
            errores.append('El nombre de usuario ya existe')
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'usuarios/form_usuario.html', {
                'usuario': usuario,
                'roles': roles
            })
        
        try:
            rol = Roles.objects.get(id_rol=rol_id)
        except Roles.DoesNotExist:
            messages.error(request, 'El rol seleccionado no existe')
            return render(request, 'usuarios/form_usuario.html', {
                'usuario': usuario,
                'roles': roles
            })
        
        # Actualizar usuario
        usuario.username = username
        usuario.rol = rol
        usuario.autenticacion = bool(autenticacion)
        usuario.save()
        
        messages.success(request, 'Usuario actualizado correctamente')
        return redirect('usuarios:lista_usuarios')
    
    return render(request, 'usuarios/form_usuario.html', {
        'usuario': usuario,
        'roles': roles
    })


@verificar_sesion
def eliminar_usuario(request, pk):
    """Vista para eliminar usuario"""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # No permitir eliminarse a sí mismo
    session_user_id = request.session.get('usuario_id')
    if session_user_id == usuario.id_usuario:
        messages.error(request, 'No puedes eliminarte a ti mismo')
        return redirect('usuarios:lista_usuarios')
    
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, 'Usuario eliminado correctamente')
        return redirect('usuarios:lista_usuarios')
    
    return render(request, 'usuarios/confirmar_eliminar.html', {
        'usuario': usuario
    })


@verificar_sesion
def cambiar_password(request, pk):
    """Vista para cambiar contraseña"""
    usuario = get_object_or_404(Usuario, pk=pk)
    
    # Verificar que sea el mismo usuario o admin
    session_user_id = request.session.get('usuario_id')
    session_rol = request.session.get('rol')
    
    if session_user_id != usuario.id_usuario and session_rol != 'admin':
        messages.error(request, 'No tienes permisos para cambiar esta contraseña')
        return redirect('usuarios:lista_usuarios')
    
    if request.method == 'POST':
        password_actual = request.POST.get('password_actual', '').strip()
        password_nueva = request.POST.get('password_nueva', '').strip()
        password_nueva_confirm = request.POST.get('password_nueva_confirm', '').strip()
        
        errores = []
        
        # Verificar contraseña actual
        if password_actual != usuario.password:
            errores.append('La contraseña actual es incorrecta')
        if len(password_nueva) < 6:
            errores.append('La nueva contraseña debe tener al menos 6 caracteres')
        if password_nueva != password_nueva_confirm:
            errores.append('Las nuevas contraseñas no coinciden')
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'usuarios/cambiar_password.html', {
                'usuario': usuario
            })
        
        # Cambiar contraseña
        usuario.password = password_nueva
        usuario.save()
        
        messages.success(request, 'Contraseña cambiada correctamente')
        return redirect('usuarios:lista_usuarios')
    
    return render(request, 'usuarios/cambiar_password.html', {
        'usuario': usuario
    })


# =============================================================================
# GESTIÓN DE ROLES
# =============================================================================

@verificar_sesion
def lista_roles(request):
    """Vista para listar roles"""
    roles = Roles.objects.all().order_by('nombre_rol')
    return render(request, 'usuarios/lista_roles.html', {
        'roles': roles
    })


@verificar_sesion
def crear_rol(request):
    """Vista para crear rol"""
    if request.method == 'POST':
        nombre_rol = request.POST.get('nombre_rol', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        
        if not nombre_rol:
            messages.error(request, 'El nombre del rol es requerido')
        elif Roles.objects.filter(nombre_rol=nombre_rol).exists():
            messages.error(request, 'El rol ya existe')
        else:
            Roles.objects.create(nombre_rol=nombre_rol, descripcion=descripcion)
            messages.success(request, 'Rol creado correctamente')
            return redirect('usuarios:lista_roles')
    
    return render(request, 'usuarios/form_rol.html')


@verificar_sesion
def dashboard_view(request):
    """Vista para renderizar el Dashboard con datos reales"""
    from apps.clientes.models import Cliente
    from apps.empleados.models import Empleado
    from apps.trabajos.models import Trabajo
    from apps.facturacion.models import Factura
    from apps.agenda.models import AgendaCita
    from django.db.models import Sum
    
    # 1. Total Clientes Activos
    total_clientes = Cliente.objects.filter(activo=True).count()
    
    # 2. Total Empleados Activos
    total_empleados = Empleado.objects.filter(activo=True).count()
    
    # 3. Trabajos en Proceso (no completados)
    trabajos_activos = Trabajo.objects.exclude(estado='completado').count()
    
    # 4. Ingresos Totales (suma del total de facturas pagadas)
    ingresos = Factura.objects.filter(estado_pago='pagada').aggregate(total=Sum('total'))['total'] or 0
    
    # 5. Citas de hoy
    hoy = timezone.now().date()
    citas_hoy = AgendaCita.objects.filter(fecha=hoy).select_related('cliente', 'empleado').order_by('hora')
    
    # 6. Facturas Pendientes
    facturas_pendientes = Factura.objects.filter(estado_pago='pendiente').select_related(
        'trabajo', 'trabajo__propiedad', 'trabajo__propiedad__cliente'
    ).order_by('-fecha_emision')[:5]
    
    # Calcular incremento mensual
    primer_dia_mes = hoy.replace(day=1)
    clientes_este_mes = Cliente.objects.filter(fecha_alta__date__gte=primer_dia_mes).count()
    total_clientes_anterior = max(total_clientes - clientes_este_mes, 1)
    porcentaje_clientes = int((clientes_este_mes / total_clientes_anterior) * 100)
    
    empleados_este_mes = Empleado.objects.filter(fecha_alta__date__gte=primer_dia_mes).count()
    total_empleados_anterior = max(total_empleados - empleados_este_mes, 1)
    porcentaje_empleados = int((empleados_este_mes / total_empleados_anterior) * 100)
    
    ingresos_este_mes = Factura.objects.filter(estado_pago='pagada', fecha_creacion__date__gte=primer_dia_mes).aggregate(total=Sum('total'))['total'] or 0
    ingresos_anterior = max(float(ingresos) - float(ingresos_este_mes), 1)
    porcentaje_ingresos = int((float(ingresos_este_mes) / ingresos_anterior) * 100)

    return render(request, 'dashboard.html', {
        'total_clientes': total_clientes,
        'total_empleados': total_empleados,
        'trabajos_activos': trabajos_activos,
        'ingresos': ingresos,
        'citas_hoy': citas_hoy,
        'facturas_pendientes': facturas_pendientes,
        'porcentaje_clientes': porcentaje_clientes,
        'porcentaje_empleados': porcentaje_empleados,
        'porcentaje_ingresos': porcentaje_ingresos,
    })
