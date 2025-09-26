# core/views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from .models import Usuario
import json


# --------- Helpers ---------
def _load_json(request):
    """
    Carga el cuerpo JSON de la request de forma segura.
    Devuelve (data, error) donde error es un string o None.
    """
    try:
        return json.loads(request.body or "{}"), None
    except Exception:
        return None, "JSON inválido."


def _s(val):
    """Trim solo si es string."""
    return val.strip() if isinstance(val, str) else val


# ========== CREATE ==========
@csrf_exempt
def registrar_usuario(request):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)

    data, err = _load_json(request)
    if err:
        return JsonResponse({'success': False, 'error': err}, status=400)

    # Requeridos
    requeridos = ['nombre', 'apellidos', 'correo', 'direccion', 'telefono', 'clave', 'rol']
    faltan = [k for k in requeridos if k not in data]
    if faltan:
        return JsonResponse({'success': False, 'error': f'Faltan campos: {", ".join(faltan)}'}, status=400)

    # Normalizar/validar strings
    nombre     = _s(data.get('nombre'))
    apellidos  = _s(data.get('apellidos'))
    correo     = _s(data.get('correo'))
    direccion  = _s(data.get('direccion'))
    telefono   = _s(data.get('telefono'))
    clave      = _s(data.get('clave'))
    rol_raw    = data.get('rol')

    vacios = [k for k, v in [
        ('nombre', nombre), ('apellidos', apellidos), ('correo', correo),
        ('direccion', direccion), ('telefono', telefono), ('clave', clave)
    ] if not v]
    if vacios:
        return JsonResponse({'success': False, 'error': f'Campos vacíos: {", ".join(vacios)}'}, status=400)

    # Rol numérico y válido
    try:
        rol = int(rol_raw)
        if rol not in (1, 2, 3, 4, 5):
            return JsonResponse({'success': False, 'error': 'Rol inválido.'}, status=400)
    except Exception:
        return JsonResponse({'success': False, 'error': 'Rol debe ser numérico.'}, status=400)

    # Correo único (case-insensitive)
    correo = correo.lower()
    if Usuario.objects.filter(correo=correo).exists():
        return JsonResponse({'success': False, 'error': 'El correo ya está registrado.'}, status=409)

    # Crear
    try:
        Usuario.objects.create(
            nombre=nombre,
            apellidos=apellidos,
            correo=correo,
            direccion=direccion,
            telefono=telefono,
            rol=rol,
            contrasena=make_password(clave),
        )
        return JsonResponse({'success': True, 'mensaje': 'Usuario registrado correctamente en Oracle.'}, status=201)
    except Exception as e:
        # Si aparece ORA-00904 u otro error de columnas, la tabla no coincide con el modelo.
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


# ========== READ / LOGIN ==========
@csrf_exempt
def iniciar_sesion(request):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)

    data, err = _load_json(request)
    if err:
        return JsonResponse({'success': False, 'error': err}, status=400)

    correo = _s(data.get('correo', '')).lower() if data.get('correo') else ''
    clave  = _s(data.get('clave', '')) if data.get('clave') else ''

    if not correo or not clave:
        return JsonResponse({'success': False, 'error': 'Correo y contraseña son obligatorios.'}, status=400)

    try:
        usuario = Usuario.objects.get(correo=correo)
    except Usuario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'El correo no está registrado.'}, status=404)

    if not check_password(clave, usuario.contrasena):
        return JsonResponse({'success': False, 'error': 'Contraseña incorrecta.'}, status=401)

    # Guardar datos en sesión
    request.session['usuario_id'] = usuario.id
    request.session['usuario_nombre'] = usuario.nombre
    request.session['usuario_apellidos'] = usuario.apellidos
    request.session['usuario_correo'] = usuario.correo
    request.session['usuario_direccion'] = usuario.direccion
    request.session['usuario_telefono'] = usuario.telefono
    request.session['usuario_rol'] = usuario.rol

    # Mapa de rol -> nombre de URL
    ROL_TO_URLNAME = {
        1: 'superusuario',      # /core/superusuario/  (core/urls.py)
        2: 'Admin',             # /Cursos/Admin/       (biblioteca/urls.py)
        3: 'Cursos',            # /Cursos/             (biblioteca/urls.py)
        4: 'profesor_perfil',   # /profesor-perfil/    (biblioteca/urls.py)
        5: 'Alumno',            # /Cursos/Alumno/      (biblioteca/urls.py)
    }
    try:
        next_url = reverse(ROL_TO_URLNAME.get(usuario.rol, 'Cursos'))
    except Exception:
        # Si no existe la ruta, mejor regresar éxito sin next_url para que el front decida.
        next_url = None

    return JsonResponse({'success': True, 'rol': usuario.get_rol_display(), 'next_url': next_url})


# ========== UPDATE ==========
@csrf_exempt
def modificar_perfil(request):
    if request.method != "POST":
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

    data, err = _load_json(request)
    if err:
        return JsonResponse({'success': False, 'error': err}, status=400)

    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        return JsonResponse({'success': False, 'error': 'Usuario no autenticado'}, status=401)

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Usuario no encontrado'}, status=404)

    # Actualizar campos si vienen
    nombre    = _s(data.get('nombre')) if data.get('nombre') is not None else None
    apellidos = _s(data.get('apellidos')) if data.get('apellidos') is not None else None
    direccion = _s(data.get('direccion')) if data.get('direccion') is not None else None
    telefono  = _s(data.get('telefono')) if data.get('telefono') is not None else None
    nueva_clave = _s(data.get('clave')) if data.get('clave') is not None else None

    if nombre is not None:
        usuario.nombre = nombre or usuario.nombre
    if apellidos is not None:
        usuario.apellidos = apellidos or usuario.apellidos
    if direccion is not None:
        usuario.direccion = direccion or usuario.direccion
    if telefono is not None:
        usuario.telefono = telefono or usuario.telefono
    if nueva_clave:
        usuario.contrasena = make_password(nueva_clave)

    usuario.save()
    return JsonResponse({'success': True, 'mensaje': 'Perfil actualizado correctamente'})


# ========== DELETE ==========
@csrf_exempt
def eliminar_usuario(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Método no permitido."}, status=405)

    # Aceptar JSON {"id": 123} o form-data id=123
    data, _ = _load_json(request)
    usuario_id = (data or {}).get("id") or request.POST.get("id")

    if not usuario_id:
        return JsonResponse({"success": False, "error": "El campo id es obligatorio."}, status=400)

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return JsonResponse({"success": False, "error": "Usuario no encontrado."}, status=404)

    usuario.delete()
    return JsonResponse({"success": True, "mensaje": f"Usuario con id {usuario_id} eliminado correctamente."})


# ========== PASSWORD RESET (simple) ==========
@csrf_exempt
def recuperar_clave(request):
    if request.method == "POST":
        data, err = _load_json(request)
        if err:
            return JsonResponse({'success': False, 'error': err}, status=400)

        correo = _s(data.get('correo', '')).lower() if data.get('correo') else ''
        if not correo:
            return JsonResponse({'success': False, 'error': 'Correo es obligatorio.'}, status=400)

        try:
            usuario = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            # Para no filtrar correos válidos/ inválidos, podrías devolver 200 genérico
            return JsonResponse({'success': False, 'error': 'Correo no encontrado.'}, status=404)

        uidb64 = urlsafe_base64_encode(force_bytes(usuario.pk))
        reset_url = f'http://127.0.0.1:8000/restablecer/{uidb64}/'

        # Asegúrate de tener EMAIL_* configurado en settings.py
        send_mail(
            'Restablecimiento de contraseña',
            f'Para restablecer tu contraseña, haz clic en: {reset_url}',
            'no-reply@tudominio.com',
            [correo],
            fail_silently=True,  # evita romper si falta config de email en dev
        )

        return JsonResponse({'success': True, 'mensaje': 'Correo enviado con instrucciones.'})

    # Si quieres una página HTML para ingresar el correo:
    return render(request, 'recuperar_clave.html')


# ========== SUPERADMIN DASHBOARD ==========
def superadmin_dashboard(request):
    # Solo rol=1
    if request.session.get("usuario_rol") != 1:
        return redirect("Sesion")  # /Cursos/Sesion/

    usuarios = Usuario.objects.all()
    return render(request, "superusuario.html", {"usuarios": usuarios, "usuario_nombre": request.session.get("usuario_nombre")})
