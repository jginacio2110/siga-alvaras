from django.contrib import admin
from django.urls import path
from cadastro.views import tela_login, painel, cadastrar, pesquisar

urlpatterns = [
    path('', tela_login),
    path('painel/', painel),
    path('cadastrar/', cadastrar),
    path('pesquisar/', pesquisar),
    path('admin/', admin.site.urls),
]