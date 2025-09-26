from django.db import models

# Create your models here.
class Idiomas(models.Model):
    nombre = models.CharField(max_length=200)
    
def __str__(self):
    return self.nombre

class Asignaturas(models.Model):
    codigo_asignatura = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    nivel = models.CharField(max_length=100)
    profesor = models.CharField(max_length=100)
    horario = models.CharField(max_length=200)
    categoria = models.ForeignKey(Idiomas, on_delete=models.CASCADE, related_name='asignaturas')

def __str__(self):
    return self.nombre

class Usuario(models.Model):
    nombre    = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo    = models.EmailField(unique=True)
    direccion = models.CharField(max_length=200)
    telefono  = models.CharField(max_length=20)

    ROL_CHOICES = [
        (1, 'superusuario'),
        (2, 'administrador'),
        (3, 'invitado'),
        (4, 'profesor'),
        (5, 'alumno'),
    ]
    rol = models.IntegerField(choices=ROL_CHOICES, default=5)

    contrasena = models.CharField(max_length=128)  

    def __str__(self):
        return f"{self.nombre} {self.apellidos}"