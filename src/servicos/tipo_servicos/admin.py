from django.contrib import admin

from cadastros.empresas.admin import BaseAssociadoEmpresaAdmin
from servicos.tipo_servicos.models import TipoServico


@admin.register(TipoServico)
class TipoServicoAdmin(BaseAssociadoEmpresaAdmin):
    search_fields = "nome", 
    search_help_text = "Nome..."

    def get_list_display(self, request):
        base_list = list(super().get_list_display(request))

        new_list = ["nome", ]

        return new_list + base_list

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
