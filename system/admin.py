from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Pessoa, Entrega, GrupoEntrega

@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    list_display = ('id','nome', 'cpf', 'grupo', 'telefone')
    search_fields = ('nome', 'cpf', 'nis', 'rg')

@admin.register(GrupoEntrega)
class GrupoEntregaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data_programada', 'status')
    list_filter = ('nome', 'status')

@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ('pessoa', 'grupo', 'entregador', 'data_entrega', 'validada')
    list_filter = ('grupo', 'validada', 'entregador')
