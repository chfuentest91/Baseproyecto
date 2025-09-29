from django.urls import path
from . import views  

urlpatterns = [
    path('Cursos/', views.Cursos, name="Cursos"),
    path('Cursos/registro/', views.registro, name="registro"),
    path('Cursos/Sesion/', views.Sesion, name="Sesion"),
    path('Cursos/Recuperar/', views.Recuperar, name="Recuperar"),
    path('Cursos/Alumno/', views.Alumno, name='Alumno'),
    path('Cursos/Admin/', views.Admin, name='Admin'),
    path('profesor-perfil/', views.profesor_perfil, name='profesor_perfil'),
    path('Carrito/', views.Carrito, name="Carrito"),
    path('superusuario/', views.superusuario, name="superusuario"),
    path('Cursos/cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    path('Cursos/mi_perfil/', views.mi_perfil, name="mi_perfil"),

    # --- Administración de usuarios (solo superusuario) ---
    path('usuarios/', views.listar_usuarios, name="listar_usuarios"),
    path('usuarios/<int:pk>/editar/', views.usuario_editar, name="usuario_editar"),
    path('usuarios/<int:pk>/eliminar/', views.usuario_eliminar, name="usuario_eliminar"),

    # --- TRADUCTOR ---
    path("traductor/", views.traductor, name="Traductor"),
    path("api/traducir/", views.api_traducir, name="api_traducir"),
]
