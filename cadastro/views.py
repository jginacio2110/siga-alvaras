from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Alvara


def tela_login(request):
    if request.method == 'POST':
        usuario = request.POST['username']
        senha = request.POST['password']

        user = authenticate(request, username=usuario, password=senha)

        if user is not None:
            login(request, user)
            return redirect('/painel')

    return render(request, 'cadastro/login.html')


@login_required
def painel(request):
    return render(request, 'cadastro/painel.html')


@login_required
def cadastrar(request):
    if request.method == 'POST':
        Alvara.objects.create(
            numero=request.POST['numero'],
            nome=request.POST['nome'],
            cnpj=request.POST['cnpj'],
            endereco=request.POST['endereco'],
            responsavel=request.POST['responsavel'],
            emissao=request.POST['emissao'],
            validade=request.POST['validade'],
            situacao=request.POST['situacao']
        )
        return redirect('/painel')

    return render(request, 'cadastro/cadastrar.html')


@login_required
def pesquisar(request):
    busca = request.GET.get('q', '')

    if busca:
        dados = (
            Alvara.objects.filter(nome__icontains=busca) |
            Alvara.objects.filter(cnpj__icontains=busca) |
            Alvara.objects.filter(numero__icontains=busca)
        )
    else:
        dados = Alvara.objects.all()

    return render(request, 'cadastro/pesquisa.html', {'dados': dados})