from django.contrib import admin
from .models import Empresa, Seguranca, PaginaSistema, PermissaoUsuario

admin.site.register(Empresa)
admin.site.register(Seguranca)
admin.site.register(PaginaSistema)
admin.site.register(PermissaoUsuario)