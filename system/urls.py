from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("beneficiarios/", views.beneficiarios_view, name="beneficiarios"),
    path("cadastro/", views.cadastro_view, name="cadastro"),
]