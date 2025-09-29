from django import forms
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from core.models import Usuario

# --- nuevos imports para el traductor ---
import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# ---------------------------------------

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



#    TRADUCTOR ONLINE


def traductor(request):
    return render(request, "traductor.html")

@csrf_exempt  
@require_POST
def api_traducir(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
        texto   = payload.get("texto", "").strip()
        origen  = payload.get("origen", "auto")   
        destino = payload.get("destino", "es")

        if not texto:
            return JsonResponse({"error": "Texto vacío."}, status=400)

        # Endpoint público de Google Translate
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": origen,
            "tl": destino,
            "dt": "t",
            "q": texto,
        }
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

       
        traduccion = "".join(seg[0] for seg in data[0] if seg and seg[0])

        return JsonResponse({
            "traduccion": traduccion,
            "origen_detectado": data[2] if len(data) > 2 else origen
        })
    except requests.exceptions.RequestException:
        return JsonResponse({"error": "No se pudo contactar el servicio de traducción."}, status=502)
    except Exception:
        return JsonResponse({"error": "Error procesando la solicitud."}, status=500)
