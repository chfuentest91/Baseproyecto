from django.urls import path
from .views import (
    Cursos, registro, Sesion, Recuperar, Alumno, Admin,
    profesor_perfil, Carrito, superusuario, cerrar_sesion, mi_perfil,
    listar_usuarios, usuario_editar, usuario_eliminar   
)

urlpatterns = [
    path('Cursos/', Cursos, name="Cursos"),
    path('Cursos/registro/', registro, name="registro"),
    path('Cursos/Sesion/', Sesion, name="Sesion"),
    path('Cursos/Recuperar/', Recuperar, name="Recuperar"),
    path('Cursos/Alumno/', Alumno, name='Alumno'),
    path('Cursos/Admin/', Admin, name='Admin'),
    path('profesor-perfil/', profesor_perfil, name='profesor_perfil'),
    path('Carrito/', Carrito, name="Carrito"),
    path('superusuario/', superusuario, name="superusuario"),
    path('Cursos/cerrar_sesion/', cerrar_sesion, name='cerrar_sesion'),
    path('Cursos/mi_perfil/', mi_perfil, name="mi_perfil"),

    # --- Administración de usuarios (solo superusuario) ---
    path('usuarios/', listar_usuarios, name="listar_usuarios"),
    path('usuarios/<int:pk>/editar/', usuario_editar, name="usuario_editar"),
    path('usuarios/<int:pk>/eliminar/', usuario_eliminar, name="usuario_eliminar"),
]
