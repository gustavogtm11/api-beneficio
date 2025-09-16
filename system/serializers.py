from rest_framework import serializers
from .models import Pessoa, Entrega, GrupoEntrega

class PessoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pessoa
        fields = "__all__"

class EntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrega
        fields = "__all__"
        read_only_fields = ["entregador", "data_entrega"]  # quem entregou e hora serão automáticos

    def create(self, validated_data):
        user = self.context['request'].user  # pega o usuário logado
        validated_data['entregador'] = user
        return super().create(validated_data)

class GrupoEntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupoEntrega
        fields = "__all__"
