from django.db import models

class Alvara(models.Model):
    numero = models.CharField(max_length=50)
    nome = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18)
    endereco = models.CharField(max_length=250)
    responsavel = models.CharField(max_length=150)
    emissao = models.DateField()
    validade = models.DateField()
    situacao = models.CharField(max_length=30)

    def __str__(self):
        return self.nome
