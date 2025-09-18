from django import forms
from .models import *

class PessoaForm(forms.ModelForm):
    class Meta:
        model = Pessoa
        fields = ["nome", "nis", "cpf","rg","endereco","integrantes_familia","telefone","grupo"]


