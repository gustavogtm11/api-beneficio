from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
from datetime import timedelta



# Create your models here.

class CustomUser(AbstractUser):
    SETORES = [
        ("adm", "Administração"),
        ("entregador", "Entregador"),
        ("cozinhas", "Cozinhas"),
        ("kitAlimentos", "Kit Alimentos"),
        ]

    setor = models.CharField(max_length=30, choices=SETORES, default="adm")

    def __str__(self):
        return f"{self.username} - {self.setor}"


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



from django.db import models
from django.utils import timezone
from datetime import timedelta

class GrupoEntrega(models.Model):
    GRUPOS = Pessoa.GRUPOS  # herdando as opções de grupo de Pessoa
    nome = models.CharField(max_length=20, choices=GRUPOS)
    data_programada = models.DateField()
    validade = models.DateField(blank=True, null=True)  # será calculada no save
    status = models.CharField(max_length=20, default="ativo")

    def save(self, *args, **kwargs):
        # Define validade se ainda não tiver
        if not self.validade and self.data_programada:
            self.validade = self.data_programada + timedelta(days=7)

        # Atualiza status com base na validade
        if self.validade and timezone.now().date() > self.validade:
            self.status = "inativo"
        else:
            self.status = "ativo"

        super().save(*args, **kwargs)

    def expirou(self):
        """Retorna True se já passou do prazo de 7 dias"""
        return self.validade and timezone.now().date() > self.validade

    def __str__(self):
        return f"{self.get_nome_display()} - {self.data_programada}"



class Entrega(models.Model):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE, related_name="entregas")
    grupo = models.ForeignKey(GrupoEntrega, on_delete=models.CASCADE, related_name="entregas")
    entregador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    data_entrega = models.DateTimeField(auto_now_add=True)  
    validada = models.BooleanField(default=False)

    def __str__(self):
        return f"Entrega {self.id} - {self.pessoa.nome} por {self.entregador}"
