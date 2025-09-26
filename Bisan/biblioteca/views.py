from django.shortcuts import render, redirect
from django.http import JsonResponse 
from core.models import Usuario


# Create your views here.

def Cursos(request):
    return render(request, 'index.html')

def registro(request):
    return render(request, 'registrar.html')

def Sesion(request):
    return render(request, 'iniciar-sesion.html')

def Recuperar(request):
    return render(request, 'recuperarcontrasena.html')

def Alumno(request):
    return render(request, 'alumno-perfil.html')

def Admin(request):
    return render(request, 'admin-perfil.html')

def profesor_perfil(request):
    return render(request, 'profesor-perfil.html')

def Carrito(request):
    return render(request, 'carrito.html')

def mi_perfil(request):
    # si no hay sesión
    if not request.session.get('usuario_id'):
        return redirect('Sesion')

    nombre_usuario = request.session.get('usuario_nombre', None)
    return render(request, 'perfil.html', {'usuario_nombre': nombre_usuario})

def recuperar(request):
    return render(request, 'recuperarcontrasena.html')

def listar_usuarios(request):
    usuarios = Usuario.objects.all()   
    return render(request, 'superusuario.html',{'usuarios': usuarios})

def cerrar_sesion(request):
    request.session.flush()
    return redirect('Cursos')

def superusuario(request):
    return render(request, 'superusuario.html')
