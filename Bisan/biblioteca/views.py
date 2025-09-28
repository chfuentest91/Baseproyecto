from django import forms
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from core.models import Usuario


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

def cerrar_sesion(request):
    request.session.flush()
    return redirect('Cursos')

def superusuario(request):
    return render(request, 'superusuario.html')



class PerfilForm(forms.ModelForm):
    nueva_contrasena = forms.CharField(
        label="Nueva contraseña",
        widget=forms.PasswordInput,
        required=False,
        min_length=8
    )

    class Meta:
        model = Usuario
        fields = ["nombre", "apellidos", "direccion", "telefono"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control", "autocomplete": "given-name"}),
            "apellidos": forms.TextInput(attrs={"class": "form-control", "autocomplete": "family-name"}),
            "direccion": forms.TextInput(attrs={"class": "form-control", "autocomplete": "street-address"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "inputmode": "tel"}),
        }

    def save(self, commit=True):
        usuario = super().save(commit=False)
        nueva = self.cleaned_data.get("nueva_contrasena")
        if nueva:
            # Tu modelo usa 'contrasena'
            usuario.contrasena = make_password(nueva) 
        if commit:
            usuario.save()
        return usuario


def mi_perfil(request):
    usuario_id = request.session.get("usuario_id")
    if not usuario_id:
        messages.error(request, "Debes iniciar sesión.")
        return redirect("Sesion")

    usuario = get_object_or_404(Usuario, pk=usuario_id)

    if request.method == "POST":
        form = PerfilForm(request.POST, instance=usuario)
        if form.is_valid():
            usuario = form.save()

            request.session["usuario_nombre"] = usuario.nombre
            request.session["usuario_apellidos"] = usuario.apellidos
            request.session["usuario_direccion"] = usuario.direccion
            request.session["usuario_telefono"] = usuario.telefono

            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("mi_perfil")
        else:
            messages.error(request, "Revisa los campos marcados.")
    else:
        form = PerfilForm(instance=usuario)

    return render(
        request,
        "perfil.html",
        {"form": form, "rol": usuario.rol, "correo": usuario.correo}
    )


def _require_superusuario(request) -> bool:
    return request.session.get("usuario_rol") == 1


class UsuarioAdminForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["nombre", "apellidos", "correo", "rol", "direccion", "telefono"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "apellidos": forms.TextInput(attrs={"class": "form-control"}),
            "correo": forms.EmailInput(attrs={"class": "form-control"}),
            "rol": forms.Select(attrs={"class": "form-select"}),
            "direccion": forms.TextInput(attrs={"class": "form-control"}),
            "telefono": forms.TextInput(attrs={"class": "form-control", "inputmode": "tel"}),
        }


def listar_usuarios(request):
    usuarios = Usuario.objects.all().order_by("-id")
    return render(request, 'superusuario.html', {'usuarios': usuarios})


def usuario_editar(request, pk: int):
    if not _require_superusuario(request):
        messages.error(request, "No tienes permisos para editar usuarios.")
        return redirect("listar_usuarios")

    obj = get_object_or_404(Usuario, pk=pk)

    if request.method == "POST":
        form = UsuarioAdminForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario actualizado correctamente.")
            return redirect("listar_usuarios")
        messages.error(request, "Revisa los campos marcados.")
    else:
        form = UsuarioAdminForm(instance=obj)

    return render(request, "usuario_editar.html", {"form": form, "obj": obj})


@require_POST
def usuario_eliminar(request, pk: int):
    if not _require_superusuario(request):
        messages.error(request, "No tienes permisos para eliminar usuarios.")
        return redirect("listar_usuarios")

    obj = get_object_or_404(Usuario, pk=pk)

    if obj.id == request.session.get("usuario_id"):
        messages.error(request, "No puedes eliminar tu propio usuario.")
        return redirect("listar_usuarios")

    obj.delete()
    messages.success(request, "Usuario eliminado correctamente.")
    return redirect("listar_usuarios")
