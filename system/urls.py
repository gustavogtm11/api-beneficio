from django.urls import path, reverse_lazy
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("beneficiarios/", views.beneficiarios_view, name="beneficiarios"),
    path("cadastro/", views.cadastro_view, name="cadastro"),
    path("logout/", LogoutView.as_view(next_page=reverse_lazy('login')), name="logout"),
    path("home/", views.home_view, name="home"),
    path("resgistrar/", views.registrar_usuario, name="registrar"),
    path("editar/", views.editarPessoa, name="editarPessoa"), 
    path("carteirinha/<int:pessoa_id>/", views.gerar_carteirinha, name="gerar_carteirinha"),
    path("api/pessoa/<uuid:uuid_code>/", views.get_pessoa_by_uuid, name="get_pessoa_by_uuid"),
    path("api/confirmar/<uuid:uuid_code>/", views.confirmar_entrega_ajax, name="confirmar_entrega_ajax"),
    path("scanner/", views.scanner, name="scanner_view"),
    ]