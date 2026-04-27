from django.contrib import admin
from django.urls import path
from cadastro.views import (
    tela_login, painel, cadastrar, pesquisar, fiscalizacao,
    permissoes, sem_permissao,
    editar_empresa, editar_seguranca,
    excluir_empresa, excluir_seguranca,
    usuarios, aplicar_nivel,
    logs, exportar_logs,
    alternar_usuario, excluir_usuario,
    alterar_senha, registrar,
    pesquisar_empresa, pesquisar_seguranca,
    meus_dados, carteirinha, teste_grade_carteirinha, adicionar_ba, buscar_vigilantes
)

urlpatterns = [
    path('fiscalizacao/', fiscalizacao),
    path('fiscalizacao/ba/', adicionar_ba),
    path('buscar-vigilantes/', buscar_vigilantes),
    path('teste-grade-carteirinha/', teste_grade_carteirinha),
    path('meus-dados/', meus_dados),
    path('carteirinha/<int:id>/', carteirinha),
    path('pesquisar-empresa/', pesquisar_empresa),
    path('pesquisar-seguranca/', pesquisar_seguranca),
    path('alterar-senha/', alterar_senha),
    path('registrar/', registrar),
    path('', tela_login),
    path('painel/', painel),
    path('cadastrar/', cadastrar),
    path('pesquisar/', pesquisar),

    # 🔐 PERMISSÕES E USUÁRIOS
    path('permissoes/', permissoes),
    path('usuarios/', usuarios),
    path('aplicar-nivel/<int:usuario_id>/<str:nivel>/', aplicar_nivel),
    path('alternar-usuario/<int:id>/', alternar_usuario),
    path('excluir-usuario/<int:id>/', excluir_usuario),

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