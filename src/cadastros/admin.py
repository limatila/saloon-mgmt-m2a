from django.contrib import admin

from cadastros.models import (
    Cliente,
    Trabalhador,
    Servico
)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    pass

@admin.register(Trabalhador)
class TrabalhadorAdmin(admin.ModelAdmin):
    pass

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    pass