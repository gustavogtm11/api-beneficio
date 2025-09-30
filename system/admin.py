from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

# Seus models
from .models import Pessoa, Entrega, GrupoEntrega, CustomUser

# -----------------------
# Pessoa
# -----------------------
@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'cpf', 'grupo', 'telefone')
    search_fields = ('nome', 'cpf', 'nis', 'rg')

# -----------------------
# GrupoEntrega
# -----------------------
@admin.register(GrupoEntrega)
class GrupoEntregaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data_programada', 'status', 'validade')
    list_filter = ('nome', 'status', 'validade')

# -----------------------
# Entrega
# -----------------------
@admin.register(Entrega)
class EntregaAdmin(admin.ModelAdmin):
    list_display = ('pessoa', 'grupo', 'entregador', 'data_entrega', 'validada')
    list_filter = ('grupo', 'validada', 'entregador')

# -----------------------
# CustomUser
# -----------------------
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'setor', 'is_active', 'is_staff', 'is_superuser')
    list_filter = ('setor', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('username',)

    # Campos para criar usuário novo (com senha hash automática)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'setor'),
        }),
    )
