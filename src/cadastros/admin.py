from django.contrib import admin

from core.admin import BaseAdmin, PersonAdmin

from cadastros.models import (
    Cliente,
    Trabalhador,
    Servico
)


@admin.register(Cliente)
class ClienteAdmin(PersonAdmin):
    pass


@admin.register(Trabalhador)
class TrabalhadorAdmin(PersonAdmin):
    pass


@admin.register(Servico)
class ServicoAdmin(BaseAdmin):
    search_fields = "nome",
    search_help_text = "Nome..."

    def get_fieldsets(self, request, obj = ...):
        base_fieldsets = list(super().get_fieldsets(request, obj))
        
        new_fieldsets = [
            (
                "Basic",
                {
                    'fields': ('nome', 'preco')
                }
            ),
        ]
        
        return base_fieldsets + new_fieldsets
