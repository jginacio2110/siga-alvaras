from django.db import models
from django.contrib.auth.models import User


class Empresa(models.Model):
    cnpj = models.CharField(max_length=18, unique=True)
    nome = models.CharField(max_length=200)
    endereco = models.CharField(max_length=250)
    situacao = models.CharField(max_length=30, default='Ativa')

    def __str__(self):
        return f"{self.nome} - {self.cnpj}"


class Seguranca(models.Model):
    cpf = models.CharField(max_length=14, unique=True)
    nome_completo = models.CharField(max_length=200)
    empresa = models.ForeignKey(Empresa, on_delete=models.SET_NULL, null=True, blank=True)
    situacao = models.CharField(max_length=30, default='Ativo')

    def __str__(self):
        return self.nome_completo


# 🔐 PÁGINAS DO SISTEMA
class PaginaSistema(models.Model):
    nome = models.CharField(max_length=100)
    rota = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nome


# 🔐 PERMISSÃO POR USUÁRIO
class PermissaoUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    pagina = models.ForeignKey(PaginaSistema, on_delete=models.CASCADE)
    liberado = models.BooleanField(default=False)

    class Meta:
        unique_together = ('usuario', 'pagina')

    def __str__(self):
        return f"{self.usuario.username} - {self.pagina.nome}"
    
class LogAcao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    acao = models.CharField(max_length=100)
    descricao = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario} - {self.acao} - {self.data}"