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
    beneficiarios = Pessoa.objects.all()
    return render(request, "beneficiarios.html" ,{"beneficiarios": beneficiarios})

@login_required
def cadastro_view(request):
    grupos = Pessoa.GRUPOS
    if request.method == "POST":
        nome = request.POST.get("nome")
        nis = request.POST.get("nis")
        cpf = request.POST.get("cpf")
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
    return render(request, "cadastro.html", {"grupos": grupos})

def home_view(request):
    return render(request, "home.html")

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

    # Cria resposta HTTP como PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="carteirinha_{pessoa.id}.pdf"'

    # Cria canvas no tamanho ID-1
    c = canvas.Canvas(response, pagesize=ID_1)
    width, height = ID_1

    # Desenha borda
    margem = 0.5 * mm  # margem mínima para o recorte
    c.setLineWidth(0.3)  # deixa a linha fina
    c.rect(margem, margem, width - 2*margem, height - 2*margem)

    #background
    
    image_path = os.path.join(settings.BASE_DIR, "static", "img", "ImgAssistencia.png")
    img = Image.open(image_path).convert("RGBA")

    # Define transparência
    alpha = 60  # 0 = invisível, 255 = opaco
    img.putalpha(alpha)

    # Junta com fundo branco
    background_white = Image.new("RGB", img.size, (255, 255, 255))
    img = Image.alpha_composite(background_white.convert("RGBA"), img)

    # Salva em memória
    from io import BytesIO
    img_io = BytesIO()
    img.save(img_io, format="PNG")
    img_io.seek(0)

    background = ImageReader(img_io)

    # Centralizado e menor
    bg_width = width * 0.8
    bg_height = height * 0.8
    x = (width - bg_width) / 2
    y = (height - bg_height) / 2

    c.drawImage(background, x, y, width=bg_width, height=bg_height)

    # Nome da pessoa
    nome = pessoa.nome.upper()
    font_name = "Times-Bold"
    font_size = 13
    c.setFont(font_name, font_size)

# Mede a largura do texto
    text_width = c.stringWidth(nome, font_name, font_size)

# Se for maior que a largura da página menos margens, diminui a fonte
    max_width = width - 40  # margem de 20px cada lado
    while text_width > max_width and font_size > 6:
        font_size -= 1
        text_width = c.stringWidth(nome, font_name, font_size)

# Aplica fonte ajustada
    c.setFont(font_name, font_size)
    c.drawCentredString(width / 2, height - 20, nome)

    # Exemplo de texto adicional
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, height - 33, f"Composição: {pessoa.integrantes_familia}")
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, height - 46, f"NIS: {pessoa.nis}")

    # Geração de QR Code com informações da pessoa
    qr_code = qr.QrCodeWidget(str(pessoa.qrcode))
    bounds = qr_code.getBounds()
    size = 90  # tamanho em mm
    w = bounds[2] - bounds[0]
    h = bounds[3] - bounds[1]
    d = Drawing(size, size, transform=[size/w, 0, 0, size/h, 0, 0])
    d.add(qr_code)

    renderPDF.draw(d, c, width - 165, 17)  # posiciona no canto direito

    # Finaliza PDF
    c.showPage()
    c.save()

    return response


@login_required
def editarPessoa(request):
    pessoas = Pessoa.objects.all()

    return render(request, "editarPessoa.html" , {"pessoas": pessoas})

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
        pessoa = Pessoa.objects.get(qrcode=uuid_code)
        grupo = GrupoEntrega.objects.filter(status="ativo").first()
        if not grupo:
            return JsonResponse({"success": False, "error": "Nenhum grupo de entrega ativo."}, status=400)

        elif pessoa not in [entrega.pessoa for entrega in grupo.entregas.all()]:
            return JsonResponse({"success": False, "error": "Beneficiário não pertence ao grupo de entrega ativo."}, status=400)

        

        entrega = Entrega.objects.create(
            pessoa=pessoa,
            grupo=grupo,
            entregador=request.user,
            validada=True
        )
        return JsonResponse({"success": True, "message": f"Entrega confirmada para {pessoa.nome}"})
    except Pessoa.DoesNotExist:
        return JsonResponse({"success": False, "error": "Beneficiário não encontrado."}, status=404)

@login_required
def scanner(request):
    return render(request, "scanner.html")