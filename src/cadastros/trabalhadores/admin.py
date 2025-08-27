from django.contrib import admin

from core.pessoas.admin import PessoaAdmin
from cadastros.trabalhadores.models import Trabalhador


@admin.register(Trabalhador)
class TrabalhadorAdmin(PessoaAdmin):
    pass