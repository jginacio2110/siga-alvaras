from django.contrib import admin
from django.urls import path
from cadastro.views import (
    tela_login, painel, cadastrar, pesquisar,
    permissoes, sem_permissao,
    editar_empresa, editar_seguranca,
    excluir_empresa, excluir_seguranca,
    usuarios, aplicar_nivel,
    logs, exportar_logs
)

urlpatterns = [
    path('', tela_login),
    path('painel/', painel),
    path('cadastrar/', cadastrar),
    path('pesquisar/', pesquisar),

    # 🔐 PERMISSÕES E USUÁRIOS
    path('permissoes/', permissoes),
    path('usuarios/', usuarios),
    path('aplicar-nivel/<int:usuario_id>/<str:nivel>/', aplicar_nivel),

    # 🔐 SEGURANÇA
    path('sem-permissao/', sem_permissao),

    # ✏️ EDIÇÃO
    path('editar-empresa/<int:id>/', editar_empresa),
    path('editar-seguranca/<int:id>/', editar_seguranca),

    # 🗑️ EXCLUSÃO
    path('excluir-empresa/<int:id>/', excluir_empresa),
    path('excluir-seguranca/<int:id>/', excluir_seguranca),

    # ⚙️ ADMIN
    path('admin/', admin.site.urls),
]

urlpatterns = [
    path('', tela_login),
    path('painel/', painel),
    path('cadastrar/', cadastrar),
    path('pesquisar/', pesquisar),

    # 🔐 PERMISSÕES E USUÁRIOS
    path('permissoes/', permissoes),
    path('usuarios/', usuarios),
    path('aplicar-nivel/<int:usuario_id>/<str:nivel>/', aplicar_nivel),

    # 📊 LOGS
    path('logs/', logs),
    path('exportar-logs/', exportar_logs),

    # 🔐 SEGURANÇA
    path('sem-permissao/', sem_permissao),

    # ✏️ EDIÇÃO
    path('editar-empresa/<int:id>/', editar_empresa),
    path('editar-seguranca/<int:id>/', editar_seguranca),

    # 🗑️ EXCLUSÃO
    path('excluir-empresa/<int:id>/', excluir_empresa),
    path('excluir-seguranca/<int:id>/', excluir_seguranca),

    # ⚙️ ADMIN
    path('admin/', admin.site.urls),
]