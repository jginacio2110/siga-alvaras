from django.core.management.base import BaseCommand
from cadastro.models import Municipio

class Command(BaseCommand):
    help = 'Importa municípios básicos'

    def handle(self, *args, **kwargs):
        lista = [
            "Porto Alegre",
            "Canoas",
            "Caxias do Sul",
            "Pelotas",
            "Santa Maria",
            "Gravataí",
            "Viamão",
            "Novo Hamburgo",
            "São Leopoldo",
            "Rio Grande"
        ]

        for nome in lista:
            Municipio.objects.get_or_create(nome=nome)

        self.stdout.write(self.style.SUCCESS('Municípios importados com sucesso!'))