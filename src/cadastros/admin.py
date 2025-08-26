from django.contrib import admin

from cadastros.models import (
    Cliente,
    Trabalhador,
    Servico
)
from core.admin import PersonAdmin

@admin.register(Cliente)
class ClienteAdmin(PersonAdmin):
    pass

@admin.register(Trabalhador)
class TrabalhadorAdmin(PersonAdmin):
    pass

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    pass