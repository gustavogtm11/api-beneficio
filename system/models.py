from django.db import models
import uuid
from django.contrib.auth.models import User

# Create your models here.

class Pessoa(models.Model):
    GRUPOS = [
        ("mensal", "Mensal"),
        ("bimestral", "Bimestral"),
        ("outro", "Outro"),
    ]
    nome = models.CharField(max_length=150)
    nis = models.CharField(max_length=11, unique=True)
    cpf = models.CharField(max_length=11, unique=True)
    rg = models.CharField(max_length=20, unique=True)
    endereco = models.CharField(max_length=255)
    integrantes_familia = models.IntegerField(default=1)
    telefone = models.CharField(max_length=15)
    grupo = models.CharField(max_length=20, choices=GRUPOS, default="outro")
    qrcode = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    def __str__(self):
        return f"{self.nome} - {self.nis}"

class GrupoEntrega(models.Model):
    GRUPOS = Pessoa.GRUPOS  # 🔹 herdando as opções de grupo de Pessoa

    nome = models.CharField(max_length=20, choices=GRUPOS) 
    data_programada = models.DateField() 
    status = models.CharField(max_length=20, default="ativo")
    def __str__(self):
        return f"{self.get_nome_display()} - {self.data_programada}"

class Entrega(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name="entregas")
    grupo = models.ForeignKey(GrupoEntrega, on_delete=models.CASCADE, related_name="entregas")
    entregador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    data_entrega = models.DateTimeField(auto_now_add=True)  
    validada = models.BooleanField(default=False)

    def __str__(self):
        return f"Entrega {self.id} - {self.pessoa.nome} por {self.entregador}"
