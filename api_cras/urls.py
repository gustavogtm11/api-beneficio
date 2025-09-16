from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from system.views import PessoaViewSet, EntregaViewSet, GrupoEntregaViewSet

router = routers.DefaultRouter()

router.register(r'pessoas', PessoaViewSet)
router.register(r'entregas', EntregaViewSet)
router.register(r'grupos', GrupoEntregaViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api', include(router.urls)),
]