from django.db import models
from django.contrib.auth.models import User


class Municipio(models.Model):
    nome = models.CharField(max_length=100)
    estado = models.CharField(max_length=2, default='RS')

    class Meta:
        ordering = ['nome']
        verbose_name = 'Município'
        verbose_name_plural = 'Municípios'

    def __str__(self):
        return f"{self.nome} - {self.estado}"


class Empresa(models.Model):
    TIPO_PESSOA = [
        ('fisica', 'Pessoa Física'),
        ('juridica', 'Pessoa Jurídica'),
    ]

    tipo_pessoa = models.CharField(max_length=20, choices=TIPO_PESSOA, default='juridica')

    razao_social = models.CharField(max_length=150)
    cnpj = models.CharField(max_length=18, blank=True, null=True)

    cep = models.CharField(max_length=9, blank=True, null=True)
    endereco = models.CharField(max_length=150)
    numero = models.CharField(max_length=20, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)

    municipio = models.ForeignKey(
        Municipio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    estado = models.CharField(max_length=2, default='RS')

    proprietario = models.CharField(max_length=150, blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True, null=True)
    rg = models.CharField(max_length=20, blank=True, null=True)

    situacao = models.CharField(max_length=20, default='Ativa')

    def __str__(self):
        return self.razao_social


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