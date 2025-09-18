from rest_framework import viewsets
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from .serializers import *
from django.contrib.auth.decorators import login_required
from .forms import *



class PessoaViewSet(viewsets.ModelViewSet):
    queryset = Pessoa.objects.all()
    serializer_class = PessoaSerializer

    


class EntregaViewSet(viewsets.ModelViewSet):
    queryset = Entrega.objects.all()
    serializer_class = EntregaSerializer


class GrupoEntregaViewSet(viewsets.ModelViewSet):
    queryset = GrupoEntrega.objects.all()
    serializer_class = GrupoEntregaSerializer
# Create your views here.


@login_required
def index(request):
        return render(request, "index.html")

def login_view(request):
    if request.user.is_authenticated:
        return redirect("index")  
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username,     password=password)
        if user is not None:
            login(request, user)
            return redirect("index")  # redireciona para a página inicial após o login
        else:
            messages.error(request, "Credenciais inválidas. Tente novamente.")
    return render(request, "login.html")

@login_required
def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def beneficiarios_view(request):
    return render(request, "beneficiarios.html")

@login_required
def cadastro_view(request):
    if request.method == "POST":
        form = PessoaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("beneficiarios")
        else:
            messages.error(request, "Erro no formulário. Verifique os dados e tente novamente.")
    else:
        form = PessoaForm()
    return render(request, "cadastro.html", {"form": form})