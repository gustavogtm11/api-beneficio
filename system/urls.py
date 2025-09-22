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
]