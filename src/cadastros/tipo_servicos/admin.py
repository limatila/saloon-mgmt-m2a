from django.contrib import admin

from core.bases.admin import BaseAssociadoEmpresaAdmin
from cadastros.tipo_servicos.models import TipoServico

@admin.register(TipoServico)
class TipoServicoAdmin(BaseAssociadoEmpresaAdmin):
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
