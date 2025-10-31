from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from .serializers import *
from django.contrib.auth.decorators import login_required
from .forms import *
import qrcode
from io import BytesIO
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from django.http import HttpResponse, Http404, JsonResponse
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.lib.utils import ImageReader
import os
import urllib.request
from django.conf import settings
from PIL import Image, ImageEnhance
from datetime import timedelta
from django.utils import timezone
from reportlab.lib import colors
import re





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

@login_required
def dados(request):
    data = {
        "kit_alimentos":Pessoa.objects.filter(beneficio="kit_alimentos").count(),
        "cozinhaMaeCreuza":Pessoa.objects.filter(beneficio="cozinhaMaeCreuza").count(),
        "cozinhaIrmaFrancisca":Pessoa.objects.filter(beneficio="cozinhaIrmaFrancisca").count(),
        "ouro":Pessoa.objects.filter(beneficio="ouro").count(), 
        "entregasEfetuadas": Entrega.objects.filter(validada=True).count(),
        "entregasPendentes" : Entrega.objects.filter(validada=False).count(),
    }
    return JsonResponse(data)

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
    beneficiarios = Pessoa.objects.all()
    return render(request, "beneficiarios.html" ,{"beneficiarios": beneficiarios})

@login_required
def cadastro_view(request):
    grupos = Pessoa.GRUPOS
    user = request.user
    
    if user.setor == "adm":
        beneficios = Pessoa.BENEFICIO
    elif user.setor == "cozinhas":
        beneficios = [
            ("cozinhaMaeCreuza", "Cozinha Mãe Creuza"),
            ("cozinhaIrmaFrancisca", "Cozinha Irmã Francisca"),
        ]
    elif user.setor == "kitAlimentos":
        beneficios = [
            ("kit_alimentos", "Kit Alimentos"),
        ]
    else:
        beneficios = []
    
    if request.method == "POST":
        nome = request.POST.get("nome")
        nis = re.sub(r"\D", "", request.POST.get("nis"))
        cpf = re.sub(r"\D", "", request.POST.get("cpf"))  # \D = qualquer coisa que não seja número
        rg = request.POST.get("rg")
        telefone = request.POST.get("telefone")
        endereco = request.POST.get("endereco")
        componentes = request.POST.get("componentes")
        grupo = request.POST.get("grupo")


        Pessoa.objects.create(
            nome=nome,
            nis=nis,
            cpf=cpf,
            rg=rg,
            endereco=endereco,
            integrantes_familia=componentes,
            telefone=telefone,
            grupo=grupo,
        )
        messages.success(request, "Beneficiário cadastrado com sucesso!")
        return redirect("cadastro")  # Redireciona para a mesma página ou outra
    return render(request, "cadastro.html", {"grupos": grupos, "beneficios": beneficios})


@login_required
def registrar_usuario(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário criado com sucesso!")
            return redirect("registrar")
    else:
        form = CustomUserCreationForm()
    return render(request, "registrar.html", {"form": form})



# Definindo tamanho ID-1 (cartão de crédito) em mm
ID_1 = (85.60 * mm, 53.98 * mm)
def gerar_carteirinha(request, pessoa_id):
    try:
        pessoa = Pessoa.objects.get(pk=pessoa_id)
    except Pessoa.DoesNotExist:
        raise Http404("Pessoa não encontrada")

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="carteirinha_{pessoa.id}.pdf"'

    c = canvas.Canvas(response, pagesize=ID_1)
    width, height = ID_1

    margem = 0.5 * mm  # margem mínima para o recorte
    c.setLineWidth(0.3)  # deixa a linha fina
    c.rect(margem, margem, width - 2*margem, height - 2*margem)

    
    image_path = os.path.join(settings.BASE_DIR, "static", "img", "ImgAssistencia.png")
    img = Image.open(image_path).convert("RGBA")

    alpha = 60  # 0 = invisível, 255 = opaco
    img.putalpha(alpha)

    background_white = Image.new("RGB", img.size, (255, 255, 255))
    img = Image.alpha_composite(background_white.convert("RGBA"), img)

    from io import BytesIO
    img_io = BytesIO()
    img.save(img_io, format="PNG")
    img_io.seek(0)

    background = ImageReader(img_io)

    bg_width = width * 0.8
    bg_height = height * 0.8
    x = (width - bg_width) / 2
    y = (height - bg_height) / 2

    c.drawImage(background, x, y, width=bg_width, height=bg_height)

    nome = pessoa.nome.upper()
    font_name = "Times-Bold"
    font_size = 13
    c.setFont(font_name, font_size)

    text_width = c.stringWidth(nome, font_name, font_size)

    max_width = width - 40  # margem de 20px cada lado
    while text_width > max_width and font_size > 6:
        font_size -= 1
        text_width = c.stringWidth(nome, font_name, font_size)
    c.setFont(font_name, font_size)
    c.drawCentredString(width / 2, height - 20, nome)
    
    c.setFillColor(colors.red)
    c.setFont("Times-Bold", 12,)
    c.drawCentredString(width / 2, height - 33, f"{pessoa.beneficio.upper()}")
    
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    
    c.drawCentredString(width / 2, height - 46, f"Composição: {pessoa.integrantes_familia}")
    c.setFont("Helvetica", 10)
    
    qr_code = qr.QrCodeWidget(str(pessoa.qrcode))
    bounds = qr_code.getBounds()
    size = 90  # tamanho em mm
    w = bounds[2] - bounds[0]
    h = bounds[3] - bounds[1]
    d = Drawing(size, size, transform=[size/w, 0, 0, size/h, 0, 0])
    d.add(qr_code)
    
    renderPDF.draw(d, c, width - 165, 17)  # posiciona no canto direito
    
    c.showPage()
    c.save()

    return response


@login_required
def editarUsuarios(request):
    pessoas = Pessoa.objects.all()
    return render(request, "editarUsuarios.html" , {"pessoas": pessoas})


@login_required
def editarPessoa(request, pessoa_id):
    grupos = Pessoa.GRUPOS
    if request.method == "POST":
        pessoa = get_object_or_404(Pessoa, pk=pessoa_id)
        pessoa.nome = request.POST.get("nome")
        pessoa.nis = request.POST.get("nis")
        pessoa.cpf = request.POST.get("cpf")
        pessoa.rg = request.POST.get("rg")
        pessoa.endereco = request.POST.get("endereco")
        pessoa.integrantes = request.POST.get("componentes")
        pessoa.telefone = request.POST.get("telefone")
        pessoa.grupo = request.POST.get("grupo")
        pessoa.save()
        
        messages.success(request, "Edições salvas com sucesso!")  # mensagem
        return redirect("listarPessoas")  # Redireciona para a mesma página ou outra
    else:
        pessoa = get_object_or_404(Pessoa, pk=pessoa_id)
    
    return render(request, "editarPessoa.html" , {"pessoa": pessoa, "grupos": grupos})

@login_required
@require_GET
def get_pessoa_by_uuid(request, uuid_code):
    try:
        pessoa = Pessoa.objects.get(qrcode=uuid_code)
        data = {
            "id": pessoa.id,
            "nome": pessoa.nome,
            "nis": pessoa.nis,
            "cpf": pessoa.cpf,
        }
        return JsonResponse({"success": True, "pessoa": data})
    except Pessoa.DoesNotExist:
        return JsonResponse({"success": False, "error": "Beneficiário não encontrado."}, status=404)


@login_required
@require_POST
def confirmar_entrega_ajax(request, uuid_code):
    try:
        # 🔎 Busca a pessoa pelo QR Code
        pessoa = Pessoa.objects.get(qrcode=uuid_code)

        hoje = timezone.now().date()

        # 🔎 Busca o grupo que esteja dentro da validade de 7 dias
        grupo = GrupoEntrega.objects.filter(
            data_programada__lte=hoje,
            data_programada__gte=hoje - timedelta(days=7),
            status="ativo"
        ).first()

        if not grupo and pessoa.nome.lower() != "gustavo" and pessoa.nome.lower() != "oliveira":
            return JsonResponse(
                {"success": False, "error": "Nenhum grupo de entrega válido nos últimos 7 dias."}, 
                status=400
            )

        # 🔄 Impede entregas duplicadas dentro do mesmo grupo
        if Entrega.objects.filter(pessoa=pessoa, grupo=grupo).exists() and pessoa.nome.lower().split()[0] not in ["gustavo", "oliveira"]:
            return JsonResponse(
                {"success": False, "error": "Entrega já registrada para este beneficiário neste grupo."}, 
                status=400
            )


        # 📦 Cria a entrega validada
        entrega = Entrega.objects.create(
            pessoa=pessoa,
            grupo=grupo,
            entregador=request.user if request.user.is_authenticated else None,
            validada=True
        )

        # 🎉 Retorno de sucesso
        return JsonResponse(
            {"success": True, "message": f"Entrega confirmada para {pessoa.nome}"}
        )

    except Pessoa.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Beneficiário não encontrado."}, 
            status=404
        )

@login_required
def scanner(request):
    return render(request, "scanner.html")


def verificar_cpf(request, cpf):
    cpf = ''.join(filter(str.isdigit, cpf))  # remove pontos e hífen
    exists = Pessoa.objects.filter(cpf=cpf).exists()
    return JsonResponse({"exists": exists})