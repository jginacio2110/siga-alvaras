from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from functools import wraps
from datetime import date
from django.contrib.staticfiles import finders
import csv

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import mm

from .models import (
    Empresa, Seguranca, Municipio, PaginaSistema,
    PermissaoUsuario, LogAcao, DadosUsuario
)

@login_required
def meus_dados(request):
    dados, _ = DadosUsuario.objects.get_or_create(usuario=request.user)

    if request.method == 'POST':
        dados.graduacao = request.POST.get('graduacao')
        dados.nome_guerra = request.POST.get('nome_guerra')
        dados.nome_completo = request.POST.get('nome_completo')
        dados.cpf = request.POST.get('cpf')
        dados.data_nascimento = request.POST.get('data_nascimento') or None
        dados.cidade_nascimento = request.POST.get('cidade_nascimento')
        dados.uf_nascimento = request.POST.get('uf_nascimento')
        dados.pai = request.POST.get('pai')
        dados.mae = request.POST.get('mae')
        dados.save()

        return redirect('/meus-dados/')

    return render(request, 'cadastro/meus_dados.html', {'dados': dados})


@login_required
def carteirinha(request, id):
    seguranca = Seguranca.objects.select_related('empresa', 'naturalidade').get(id=id)
    dados = DadosUsuario.objects.filter(usuario=request.user).first()

    hoje = date.today()

    try:
        validade = hoje.replace(year=hoje.year + 2)
    except ValueError:
        validade = hoje.replace(month=2, day=28, year=hoje.year + 2)

    def data_br(data):
        return data.strftime('%d/%m/%Y') if data else ''

    def data_split(data):
        if not data:
            return ('', '', '')
        d = data.strftime('%d')
        m = data.strftime('%m')
        a = data.strftime('%Y')
        return d, m, a

    naturalidade = ''
    if seguranca.naturalidade:
        naturalidade = f"{seguranca.naturalidade.nome} - {seguranca.naturalidade.estado}"

    assinante = ''
    if dados:
        assinante = f"{dados.graduacao or ''} - {dados.nome_guerra or ''}".strip(' -')

    modelo = finders.find('cadastro/img/modelo_carteirinha.png')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="carteirinha_{seguranca.id}.pdf"'

    p = canvas.Canvas(response, pagesize=landscape(A4))
    largura, altura = landscape(A4)

    img_w = 270 * mm
    img_h = img_w * (1000 / 2048)

    x0 = (largura - img_w) / 2
    y0 = (altura - img_h) / 2

    p.drawImage(modelo, x0, y0, width=img_w, height=img_h)

    def pos(x, y):
        px = x0 + (x / 2048) * img_w
        py = y0 + img_h - (y / 1000) * img_h
        return px, py

    def escrever(texto, x, y, tamanho=7):
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Bold", tamanho)
        p.drawString(*pos(x, y), str(texto or '').upper())

    def escrever_centro(texto, x, y, tamanho=10):
        p.setFillColor(colors.black)
        p.setFont("Helvetica-Bold", tamanho)
        px, py = pos(x, y)
        p.drawCentredString(px, py, str(texto or '').upper())

    # =====================
    # FRENTE - MAIS À DIREITA
    # =====================
    escrever(seguranca.nome_completo, 145, 380, 12)

    escrever(seguranca.empresa.razao_social, 145, 460, 12)

    escrever("VIGIA", 145, 555, 12)

    escrever(seguranca.rg, 145, 635, 10)
    escrever(seguranca.registro, 440, 635, 10)

    escrever(data_br(hoje), 145, 730, 10)
    escrever(data_br(validade), 440, 730, 10)


    # =====================
    # VERSO - PAI / MÃE AJUSTADOS
    # =====================
    escrever(seguranca.pai, 1200, 255, 12)

    escrever(seguranca.mae, 1200, 325, 12)

    escrever(naturalidade, 1325, 385, 12)


    # =====================
    # DATAS
    # =====================
    dn_d, dn_m, dn_a = data_split(seguranca.data_nascimento)
    da_d, da_m, da_a = data_split(seguranca.data_admissao)

    escrever(dn_d, 1335, 480, 10)
    escrever(dn_m, 1380, 480, 10)
    escrever(dn_a, 1425, 480, 10)

    escrever(da_d, 1810, 480, 10)
    escrever(da_m, 1850, 480, 10)
    escrever(da_a, 1890, 480, 10)


    # =====================
    # ASSINATURA
    # =====================
    escrever_centro(assinante, 1535, 820, 12)

    p.showPage()
    p.save()

    return response



@login_required
def teste_grade_carteirinha(request):
    modelo = finders.find('cadastro/img/modelo_carteirinha.png')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="teste_grade_carteirinha.pdf"'

    p = canvas.Canvas(response, pagesize=landscape(A4))
    largura, altura = landscape(A4)

    img_w = 270 * mm
    img_h = img_w * (1000 / 2048)

    x0 = (largura - img_w) / 2
    y0 = (altura - img_h) / 2

    p.drawImage(modelo, x0, y0, width=img_w, height=img_h)

    def pos(x, y):
        px = x0 + (x / 2048) * img_w
        py = y0 + img_h - (y / 1000) * img_h
        return px, py

    p.setFont("Helvetica", 5)
    p.setStrokeColor(colors.red)
    p.setFillColor(colors.red)

    # linhas verticais
    for x in range(0, 2049, 10):
        px1, py1 = pos(x, 0)
        px2, py2 = pos(x, 1000)
        p.line(px1, py1, px2, py2)
        p.drawString(px1 + 1, py1 - 8, str(x))

    # linhas horizontais
    for y in range(0, 1001, 10):
        px1, py1 = pos(0, y)
        px2, py2 = pos(2048, y)
        p.line(px1, py1, px2, py2)
        p.drawString(px1 - 18, py1, str(y))

    p.showPage()
    p.save()

    return response

def pesquisar_empresa(request):
    busca_empresa = request.GET.get('empresa', '')

    empresas = Empresa.objects.all().order_by('razao_social')
    resultado_empresas = Empresa.objects.all().order_by('razao_social')

    if busca_empresa:
        resultado_empresas = resultado_empresas.filter(
            Q(razao_social__icontains=busca_empresa) |
            Q(cnpj__icontains=busca_empresa) |
            Q(cpf__icontains=busca_empresa)
        )

    return render(request, 'cadastro/pesquisar_empresa.html', {
        'empresas': empresas,
        'resultado_empresas': resultado_empresas,
        'busca_empresa': busca_empresa,
    })


def pesquisar_seguranca(request):
    busca_cpf = request.GET.get('cpf', '')

    resultado_segurancas = Seguranca.objects.select_related('empresa').all().order_by('nome_completo')

    if busca_cpf:
        resultado_segurancas = resultado_segurancas.filter(
            Q(cpf__icontains=busca_cpf) |
            Q(nome_completo__icontains=busca_cpf)
        )

    return render(request, 'cadastro/pesquisar_seguranca.html', {
        'resultado_segurancas': resultado_segurancas,
        'busca_cpf': busca_cpf,
    })


def tem_permissao(usuario, rota):
    if not usuario.is_authenticated:
        return False

    if usuario.is_superuser:
        return True

    return PermissaoUsuario.objects.filter(
        usuario=usuario,
        pagina__rota=rota,
        liberado=True
    ).exists()


def permissao_requerida(rota):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not tem_permissao(request.user, rota):
                return redirect('/sem-permissao/')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


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
                if request.POST.get('lembrar'):
                    request.session.set_expiry(60 * 60 * 24 * 30)  # 30 dias
                else:
                    request.session.set_expiry(0)  # fecha ao sair do navegador

                LogAcao.objects.create(
                    usuario=user,
                    acao='Login',
                    descricao='Usuário fez login no sistema'
                )

                if not tem_permissao(user, 'painel'):
                    return redirect('/sem-permissao/')

                return redirect('/painel/')
        else:
            erro = "Usuário ou senha inválidos."

    return render(request, 'cadastro/login.html', {'erro': erro})


@login_required
@permissao_requerida('painel')
def painel(request):
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
@permissao_requerida('cadastrar')
def cadastrar(request):
    empresas = Empresa.objects.all().order_by('razao_social')
    municipios = Municipio.objects.all().order_by('nome')

    if request.method == 'POST':
        tipo = request.POST.get('tipo')

        if tipo == 'empresa':
            empresa = Empresa.objects.create(
                tipo_pessoa=request.POST.get('tipo_pessoa'),
                cnpj=request.POST.get('cnpj'),
                razao_social=request.POST.get('razao_social'),
                endereco=request.POST.get('endereco'),
                numero=request.POST.get('numero'),
                bairro=request.POST.get('bairro'),
                cep=request.POST.get('cep'),
                complemento=request.POST.get('complemento'),
                municipio_id=request.POST.get('municipio') if request.POST.get('estado') == 'RS' else None,
                estado=request.POST.get('estado', 'RS'),
                proprietario=request.POST.get('proprietario'),
                cpf=request.POST.get('cpf'),
                rg=request.POST.get('rg'),
            )

            LogAcao.objects.create(
                usuario=request.user,
                acao='Cadastrou empresa',
                descricao=f'Empresa: {empresa.razao_social}'
            )

            return redirect('/painel/')

        if tipo == 'seguranca':
            empresa_busca = request.POST.get('empresa_busca', '')
            cnpj = empresa_busca.split(' - ')[-1].strip()

            empresa = Empresa.objects.filter(cnpj=cnpj).first()

            if not empresa:
                messages.error(request, "Empresa não encontrada. Verifique o nome ou CNPJ.")
                return redirect('/cadastrar/')

            seguranca = Seguranca.objects.create(
                cpf=request.POST.get('cpf'),
                rg=request.POST.get('rg'),
                registro=request.POST.get('registro'),
                nome_completo=request.POST.get('nome_completo'),
                pai=request.POST.get('pai'),
                mae=request.POST.get('mae'),
                naturalidade_id=request.POST.get('naturalidade') or None,
                data_nascimento=request.POST.get('data_nascimento') or None,
                data_admissao=request.POST.get('data_admissao') or None,
                empresa=empresa
            )

            LogAcao.objects.create(
                usuario=request.user,
                acao='Cadastrou segurança',
                descricao=f'Segurança: {seguranca.nome_completo}'
            )

            return redirect('/painel/')

    return render(request, 'cadastro/cadastrar.html', {
        'empresas': empresas,
        'municipios': municipios
    })


@login_required
@permissao_requerida('pesquisar')
def pesquisar(request):
    busca_empresa = request.GET.get('empresa', '')
    busca_cpf = request.GET.get('cpf', '')

    empresas = Empresa.objects.all().order_by('razao_social')
    resultado_empresas = Empresa.objects.none()
    resultado_segurancas = Seguranca.objects.none()

    if busca_empresa:
        resultado_empresas = (
            Empresa.objects.filter(razao_social__icontains=busca_empresa)|
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
@permissao_requerida('fiscalizacao')
def fiscalizacao(request):
    busca = request.GET.get('busca', '')

    ultimas_fiscalizacoes = []

    return render(request, 'cadastro/fiscalizacao.html', {
        'busca': busca,
        'ultimas_fiscalizacoes': ultimas_fiscalizacoes
    })

@login_required
def permissoes(request):
    if not request.user.is_superuser:
        return redirect('/painel/')

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
@permissao_requerida('editar')
def editar_empresa(request, id):
    empresa = Empresa.objects.get(id=id)

    if request.method == 'POST':
        empresa.cnpj = request.POST['cnpj']
        empresa.razao_social = request.POST['razao_social']
        empresa.endereco = request.POST['endereco']
        empresa.situacao = request.POST['situacao']
        empresa.save()

        LogAcao.objects.create(
            usuario=request.user,
            acao='Editou empresa',
            descricao=f'Empresa: {empresa.razao_social}'
        )

        return redirect('/pesquisar/')

    return render(request, 'cadastro/editar_empresa.html', {'empresa': empresa})


@login_required
@permissao_requerida('editar')
def editar_seguranca(request, id):
    seguranca = Seguranca.objects.get(id=id)
    empresas = Empresa.objects.all().order_by('razao_social')
    municipios = Municipio.objects.all().order_by('nome')

    if request.method == 'POST':
        seguranca.cpf = request.POST.get('cpf')
        seguranca.nome_completo = request.POST.get('nome_completo')
        seguranca.rg = request.POST.get('rg')
        seguranca.registro = request.POST.get('registro')
        seguranca.pai = request.POST.get('pai')
        seguranca.mae = request.POST.get('mae')
        seguranca.naturalidade_id = request.POST.get('naturalidade') or None
        seguranca.data_nascimento = request.POST.get('data_nascimento') or None
        seguranca.data_admissao = request.POST.get('data_admissao') or None
        seguranca.empresa_id = request.POST.get('empresa_id')
        seguranca.situacao = request.POST.get('situacao')

        seguranca.save()

        LogAcao.objects.create(
            usuario=request.user,
            acao='Editou segurança',
            descricao=f'Segurança: {seguranca.nome_completo}'
        )

        return redirect('/pesquisar/')

    return render(request, 'cadastro/editar_seguranca.html', {
        'seguranca': seguranca,
        'empresas': empresas,
        'municipios': municipios
    })


@login_required
@permissao_requerida('excluir')
def excluir_empresa(request, id):
    empresa = Empresa.objects.get(id=id)

    if request.method == 'POST':
        nome_empresa = empresa.razao_social

        LogAcao.objects.create(
            usuario=request.user,
            acao='Excluiu empresa',
            descricao=f'Empresa: {nome_empresa}'
        )

        empresa.delete()
        return redirect('/pesquisar/')

    return render(request, 'cadastro/confirmar_exclusao.html', {
        'tipo': 'Empresa',
        'nome': empresa.razao_social
    })


@login_required
@permissao_requerida('excluir')
def excluir_seguranca(request, id):
    seguranca = Seguranca.objects.get(id=id)

    if request.method == 'POST':
        nome_seguranca = seguranca.nome_completo

        LogAcao.objects.create(
            usuario=request.user,
            acao='Excluiu segurança',
            descricao=f'Segurança: {nome_seguranca}'
        )

        seguranca.delete()
        return redirect('/pesquisar/')

    return render(request, 'cadastro/confirmar_exclusao.html', {
        'tipo': 'Segurança',
        'nome': seguranca.nome_completo
    })


@login_required
@permissao_requerida('usuarios')
def usuarios(request):
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

            rotas = ['painel', 'pesquisar']

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
                acao='Criou usuário',
                descricao=f'Usuário criado: {usuario.username} com nível consulta'
            )

            return redirect('/usuarios/')

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
        return redirect('/sem-permissao/')

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
        return redirect('/usuarios/')

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

    return redirect('/usuarios/')


@login_required
@permissao_requerida('logs')
def logs(request):
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
@permissao_requerida('logs')
def exportar_logs(request):
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
        return redirect('/sem-permissao/')

    usuario = User.objects.get(id=id)

    if usuario == request.user or usuario.is_superuser:
        return redirect('/usuarios/')

    if request.method == 'POST':
        nome = usuario.username

        LogAcao.objects.create(
            usuario=request.user,
            acao='Excluiu usuário',
            descricao=f'Usuário excluído: {nome}'
        )

        usuario.delete()
        return redirect('/usuarios/')

    return render(request, 'cadastro/confirmar_exclusao.html', {
        'tipo': 'Usuário',
        'nome': usuario.username
    })


@login_required
def alternar_usuario(request, id):
    if not request.user.is_superuser:
        return redirect('/sem-permissao/')

    usuario = User.objects.get(id=id)

    if usuario == request.user:
        return redirect('/usuarios/')

    usuario.is_active = not usuario.is_active
    usuario.save()

    LogAcao.objects.create(
        usuario=request.user,
        acao='Alterou status do usuário',
        descricao=f'{usuario.username} agora está {"ATIVO" if usuario.is_active else "INATIVO"}'
    )

    return redirect('/usuarios/')


def alterar_senha(request):
    return render(request, 'cadastro/alterar_senha.html')


def registrar(request):
    return render(request, 'cadastro/registrar.html')