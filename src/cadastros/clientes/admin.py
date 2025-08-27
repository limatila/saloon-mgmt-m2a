from django.contrib import admin

from core.pessoas.admin import PessoaAdmin
from cadastros.clientes.models import Cliente

@admin.register(Cliente)
class ClienteAdmin(PessoaAdmin):
    pass
