from rest_framework import viewsets
from .models import *
from .serializers import *

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
