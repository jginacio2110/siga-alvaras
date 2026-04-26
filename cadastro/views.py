from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from .models import Empresa, Seguranca, PaginaSistema, PermissaoUsuario, LogAcao
import csv


def tem_permissao(usuario, rota):
    if usuario.is_superuser:
        return True

    return PermissaoUsuario.objects.filter(
        usuario=usuario,
        pagina__rota=rota,
        liberado=True
    ).exists()


def tela_login(request):
    erro = None

    if request.method == 'POST':
        usuario = request.POST['username']
        senha = request.POST['password']

        user = authenticate(request, username=usuario, password=senha)

        if user is not None:
            if not user.is_active:
                erro = "Usuário desativado."
            else:
                login(request, user)

                LogAcao.objects.create(
                    usuario=user,
                    acao='Login',
                    descricao='Usuário fez login no sistema'
                )

                return redirect('/painel')
        else:
            erro = "Usuário ou senha inválidos."

    return render(request, 'cadastro/login.html', {'erro': erro})


@login_required
def painel(request):
    if not tem_permissao(request.user, 'painel'):
        return redirect('/sem-permissao')

    total_empresas = Empresa.objects.count()
    empresas_ativas = Empresa.objects.filter(situacao='Ativa').count()
    total_segurancas = Seguranca.objects.count()
    segurancas_ativos = Seguranca.objects.filter(situacao='Ativo').count()

    return render(request, 'cadastro/painel.html', {
        'total_empresas': total_empresas,
        'empresas_ativas': empresas_ativas,
        'total_segurancas': total_segurancas,
        'segurancas_ativos': segurancas_ativos,
    })


@login_required
def cadastrar(request):
    if not tem_permissao(request.user, 'cadastrar'):
        return redirect('/sem-permissao')

    empresas = Empresa.objects.all().order_by('nome')

    if request.method == 'POST':
        tipo = request.POST.get('tipo')

        if tipo == 'empresa':
            empresa = Empresa.objects.create(
                cnpj=request.POST['cnpj'],
                nome=request.POST['nome'],
                endereco=request.POST['endereco']
            )

            LogAcao.objects.create(
                usuario=request.user,
                acao='Cadastrou empresa',
                descricao=f'Empresa: {empresa.nome}'
            )

            return redirect('/painel')

        if tipo == 'seguranca':
            empresa_busca = request.POST['empresa_busca']
            cnpj = empresa_busca.split(' - ')[-1]
            empresa = Empresa.objects.get(cnpj=cnpj)

            seguranca = Seguranca.objects.create(
                cpf=request.POST['cpf'],
                nome_completo=request.POST['nome_completo'],
                empresa=empresa
            )

            LogAcao.objects.create(
                usuario=request.user,
                acao='Cadastrou segurança',
                descricao=f'Segurança: {seguranca.nome_completo}'
            )

            return redirect('/painel')

    return render(request, 'cadastro/cadastrar.html', {'empresas': empresas})


@login_required
def pesquisar(request):
    if not tem_permissao(request.user, 'pesquisar'):
        return redirect('/sem-permissao')

    busca_empresa = request.GET.get('empresa', '')
    busca_cpf = request.GET.get('cpf', '')

    empresas = Empresa.objects.all().order_by('nome')
    resultado_empresas = Empresa.objects.none()
    resultado_segurancas = Seguranca.objects.none()

    if busca_empresa:
        resultado_empresas = (
            Empresa.objects.filter(nome__icontains=busca_empresa) |
            Empresa.objects.filter(cnpj__icontains=busca_empresa)
        )

    if busca_cpf:
        resultado_segurancas = Seguranca.objects.filter(cpf__icontains=busca_cpf)

    return render(request, 'cadastro/pesquisa.html', {
        'empresas': empresas,
        'resultado_empresas': resultado_empresas,
        'resultado_segurancas': resultado_segurancas,
        'busca_empresa': busca_empresa,
        'busca_cpf': busca_cpf,
    })


@login_required
def permissoes(request):
    if not request.user.is_superuser:
        return redirect('/painel')

    usuarios = User.objects.all().order_by('username')
    paginas = PaginaSistema.objects.all().order_by('nome')
    usuario_id = request.GET.get('usuario') or request.POST.get('usuario_id')
    usuario_selecionado = None
    permissoes_marcadas = []

    if usuario_id:
        usuario_selecionado = User.objects.get(id=usuario_id)
        permissoes_marcadas = list(
            PermissaoUsuario.objects.filter(
                usuario=usuario_selecionado,
                liberado=True
            ).values_list('pagina_id', flat=True)
        )

    if request.method == 'POST':
        paginas_marcadas = request.POST.getlist('paginas')
        PermissaoUsuario.objects.filter(usuario=usuario_selecionado).delete()

        for pagina in paginas:
            PermissaoUsuario.objects.create(
                usuario=usuario_selecionado,
                pagina=pagina,
                liberado=str(pagina.id) in paginas_marcadas
            )

        return redirect(f'/permissoes/?usuario={usuario_selecionado.id}')

    return render(request, 'cadastro/permissoes.html', {
        'usuarios': usuarios,
        'paginas': paginas,
        'usuario_selecionado': usuario_selecionado,
        'permissoes_marcadas': permissoes_marcadas
    })


@login_required
def sem_permissao(request):
    return render(request, 'cadastro/sem_permissao.html')


@login_required
def editar_empresa(request, id):
    if not tem_permissao(request.user, 'editar'):
        return redirect('/sem-permissao')

    empresa = Empresa.objects.get(id=id)

    if request.method == 'POST':
        empresa.cnpj = request.POST['cnpj']
        empresa.nome = request.POST['nome']
        empresa.endereco = request.POST['endereco']
        empresa.situacao = request.POST['situacao']
        empresa.save()

        LogAcao.objects.create(
            usuario=request.user,
            acao='Editou empresa',
            descricao=f'Empresa: {empresa.nome}'
        )

        return redirect('/pesquisar')

    return render(request, 'cadastro/editar_empresa.html', {'empresa': empresa})


@login_required
def editar_seguranca(request, id):
    if not tem_permissao(request.user, 'editar'):
        return redirect('/sem-permissao')

    seguranca = Seguranca.objects.get(id=id)
    empresas = Empresa.objects.all().order_by('nome')

    if request.method == 'POST':
        seguranca.cpf = request.POST['cpf']
        seguranca.nome_completo = request.POST['nome_completo']
        seguranca.empresa_id = request.POST['empresa_id']
        seguranca.situacao = request.POST['situacao']
        seguranca.save()

        LogAcao.objects.create(
            usuario=request.user,
            acao='Editou segurança',
            descricao=f'Segurança: {seguranca.nome_completo}'
        )

        return redirect('/pesquisar')

    return render(request, 'cadastro/editar_seguranca.html', {
        'seguranca': seguranca,
        'empresas': empresas
    })


@login_required
def excluir_empresa(request, id):
    if not tem_permissao(request.user, 'excluir'):
        return redirect('/sem-permissao')

    empresa = Empresa.objects.get(id=id)

    if request.method == 'POST':
        nome_empresa = empresa.nome

        LogAcao.objects.create(
            usuario=request.user,
            acao='Excluiu empresa',
            descricao=f'Empresa: {nome_empresa}'
        )

        empresa.delete()
        return redirect('/pesquisar')

    return render(request, 'cadastro/confirmar_exclusao.html', {
        'tipo': 'Empresa',
        'nome': empresa.nome
    })


@login_required
def excluir_seguranca(request, id):
    if not tem_permissao(request.user, 'excluir'):
        return redirect('/sem-permissao')

    seguranca = Seguranca.objects.get(id=id)

    if request.method == 'POST':
        nome_seguranca = seguranca.nome_completo

        LogAcao.objects.create(
            usuario=request.user,
            acao='Excluiu segurança',
            descricao=f'Segurança: {nome_seguranca}'
        )

        seguranca.delete()
        return redirect('/pesquisar')

    return render(request, 'cadastro/confirmar_exclusao.html', {
        'tipo': 'Segurança',
        'nome': seguranca.nome_completo
    })


@login_required
def usuarios(request):
    if not tem_permissao(request.user, 'usuarios'):
        return redirect('/sem-permissao')

    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST.get('email', '')
        senha = request.POST['senha']

        try:
            validate_password(senha)

            usuario = User.objects.create_user(
                username=username,
                email=email,
                password=senha
            )

            LogAcao.objects.create(
                usuario=request.user,
                acao='Criou usuário',
                descricao=f'Usuário criado: {usuario.username}'
            )

            return redirect('/usuarios')

        except ValidationError as e:
            usuarios = User.objects.all().order_by('username')
            return render(request, 'cadastro/usuarios.html', {
                'usuarios': usuarios,
                'erro': e.messages
            })

    usuarios = User.objects.all().order_by('username')

    return render(request, 'cadastro/usuarios.html', {
        'usuarios': usuarios
    })


@login_required
def aplicar_nivel(request, usuario_id, nivel):
    if not request.user.is_superuser:
        return redirect('/sem-permissao')

    usuario = User.objects.get(id=usuario_id)

    if nivel == 'admin':
        rotas = ['painel', 'cadastrar', 'pesquisar', 'editar', 'excluir', 'usuarios', 'logs']
        usuario.is_superuser = True
        usuario.is_staff = True
        usuario.save()

    elif nivel == 'operador':
        rotas = ['painel', 'cadastrar', 'pesquisar', 'editar']
        usuario.is_superuser = False
        usuario.is_staff = False
        usuario.save()

    elif nivel == 'consulta':
        rotas = ['painel', 'pesquisar']
        usuario.is_superuser = False
        usuario.is_staff = False
        usuario.save()

    else:
        return redirect('/usuarios')

    PermissaoUsuario.objects.filter(usuario=usuario).delete()

    for rota in rotas:
        pagina, criado = PaginaSistema.objects.get_or_create(
            rota=rota,
            defaults={'nome': rota.capitalize()}
        )

        PermissaoUsuario.objects.create(
            usuario=usuario,
            pagina=pagina,
            liberado=True
        )

    LogAcao.objects.create(
        usuario=request.user,
        acao='Alterou nível de usuário',
        descricao=f'Usuário: {usuario.username} | Nível: {nivel}'
    )

    return redirect('/usuarios')


@login_required
def logs(request):
    if not tem_permissao(request.user, 'logs'):
        return redirect('/sem-permissao')

    usuario_id = request.GET.get('usuario', '')
    acao = request.GET.get('acao', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')

    logs = LogAcao.objects.all().order_by('-data')
    usuarios = User.objects.all().order_by('username')

    if usuario_id:
        logs = logs.filter(usuario_id=usuario_id)

    if acao:
        logs = logs.filter(acao__icontains=acao)

    if data_inicio:
        logs = logs.filter(data__date__gte=data_inicio)

    if data_fim:
        logs = logs.filter(data__date__lte=data_fim)

    return render(request, 'cadastro/logs.html', {
        'logs': logs,
        'usuarios': usuarios,
        'usuario_id': usuario_id,
        'acao': acao,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    })


@login_required
def exportar_logs(request):
    if not tem_permissao(request.user, 'logs'):
        return redirect('/sem-permissao')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="logs.csv"'

    writer = csv.writer(response)
    writer.writerow(['Usuário', 'Ação', 'Descrição', 'Data'])

    logs = LogAcao.objects.all().order_by('-data')

    for log in logs:
        writer.writerow([
            log.usuario.username if log.usuario else '---',
            log.acao,
            log.descricao,
            log.data.strftime('%d/%m/%Y %H:%M')
        ])

    return response


@login_required
def excluir_usuario(request, id):
    if not request.user.is_superuser:
        return redirect('/sem-permissao')

    usuario = User.objects.get(id=id)

    if usuario == request.user or usuario.is_superuser:
        return redirect('/usuarios')

    if request.method == 'POST':
        nome = usuario.username

        LogAcao.objects.create(
            usuario=request.user,
            acao='Excluiu usuário',
            descricao=f'Usuário excluído: {nome}'
        )

        usuario.delete()
        return redirect('/usuarios')

    return render(request, 'cadastro/confirmar_exclusao.html', {
        'tipo': 'Usuário',
        'nome': usuario.username
    })


@login_required
def alternar_usuario(request, id):
    if not request.user.is_superuser:
        return redirect('/sem-permissao')

    usuario = User.objects.get(id=id)

    if usuario == request.user:
        return redirect('/usuarios')

    usuario.is_active = not usuario.is_active
    usuario.save()

    LogAcao.objects.create(
        usuario=request.user,
        acao='Alterou status do usuário',
        descricao=f'{usuario.username} agora está {"ATIVO" if usuario.is_active else "INATIVO"}'
    )

    return redirect('/usuarios')