# usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from .models import Usuario


def login_view(request):
    """Vista para iniciar sesión"""
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me', False)
        
        if not username or not password:
            messages.error(request, 'Por favor ingrese usuario y contraseña')
            return render(request, 'usuarios/login.html')
        
        # Autenticar usuario
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.autenticacion:
                login(request, user)
                
                # Actualizar último login
                user.ultimo_login = timezone.now()
                user.save(update_fields=['ultimo_login'])
                
                messages.success(request, f'Bienvenido {user.username}')
                return redirect('usuarios:lista_usuarios')
            else:
                messages.error(request, 'Usuario no autorizado para iniciar sesión')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'usuarios/login.html')


def logout_view(request):
    """Vista para cerrar sesión"""
    
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente')
    return redirect('usuarios:login')


@login_required
def lista_usuarios(request):
    """Vista para listar usuarios"""
    
    usuarios = Usuario.objects.all().order_by('-fecha_registro')
    
    return render(request, 'usuarios/lista_usuarios.html', {
        'usuarios': usuarios
    })


@login_required
def crear_usuario(request):
    """Vista para crear nuevo usuario"""
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        rol = request.POST.get('rol', '').strip()
        permisos = request.POST.get('permisos', '').strip()
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
        if not rol:
            errores.append('El rol es requerido')
        
        if errores:
            for error in errores:
                messages.error(request, error)
            return render(request, 'usuarios/form_usuario.html')
        
        # Crear usuario
        usuario = Usuario.objects.create_user(
            username=username,
            password=password
        )
        usuario.rol = rol
        usuario.permisos = permisos
        usuario.autenticacion = bool(autenticacion)
        usuario.save()
        
        messages.success(request, 'Usuario creado correctamente')
        return redirect('usuarios:lista_usuarios')
    
    return render(request, 'usuarios/form_usuario.html')


@login_required
def editar_usuario(request, pk):
    """Vista para editar usuario"""
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        rol = request.POST.get('rol', '').strip()
        permisos = request.POST.get('permisos', '').strip()
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
                'usuario': usuario
            })
        
        # Actualizar usuario
        usuario.username = username
        usuario.rol = rol
        usuario.permisos = permisos
        usuario.autenticacion = bool(autenticacion)
        usuario.save()
        
        messages.success(request, 'Usuario actualizado correctamente')
        return redirect('usuarios:lista_usuarios')
    
    return render(request, 'usuarios/form_usuario.html', {
        'usuario': usuario
    })


@login_required
def eliminar_usuario(request, pk):
    """Vista para eliminar usuario"""
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        # No permitir eliminarse a sí mismo
        if request.user.id_usuario == usuario.id_usuario:
            messages.error(request, 'No puedes eliminarte a ti mismo')
            return redirect('usuarios:lista_usuarios')
        
        usuario.delete()
        messages.success(request, 'Usuario eliminado correctamente')
        return redirect('usuarios:lista_usuarios')
    
    return render(request, 'usuarios/confirmar_eliminar.html', {
        'usuario': usuario
    })


@login_required
def cambiar_password(request, pk):
    """Vista para cambiar contraseña"""
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    if request.method == 'POST':
        password_actual = request.POST.get('password_actual', '').strip()
        password_nueva = request.POST.get('password_nueva', '').strip()
        password_nueva_confirm = request.POST.get('password_nueva_confirm', '').strip()
        
        # Validaciones
        errores = []
        
        if not usuario.check_password(password_actual):
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
        usuario.set_password(password_nueva)
        usuario.save()
        
        messages.success(request, 'Contraseña cambiada correctamente')
        return redirect('usuarios:lista_usuarios')
    
    return render(request, 'usuarios/cambiar_password.html', {
        'usuario': usuario
    })


@login_required
def detalle_usuario(request, pk):
    """Vista para ver detalles de usuario"""
    
    usuario = get_object_or_404(Usuario, pk=pk)
    
    return render(request, 'usuarios/detalle_usuario.html', {
        'usuario': usuario
    })


@require_http_methods(["POST"])
def validar_username(request):
    """API para validar si username existe"""
    
    username = request.POST.get('username', '').strip()
    existe = Usuario.objects.filter(username=username).exists()
    
    return JsonResponse({
        'existe': existe,
        'mensaje': 'El nombre de usuario ya existe' if existe else 'Usuario disponible'
    })
