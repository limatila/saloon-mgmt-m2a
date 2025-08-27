from django.contrib import admin

from cadastros.empresas.models import Empresa
from core.bases.admin import DateHierarchyAdmin


@admin.register(Empresa)
class EmpresaAdmin(DateHierarchyAdmin):
    search_fields = "cnpj", "nome_fantasia", "razao_social"
    search_help_text = "CNPJ, nome fantasia ou razao social..."

    def get_fieldsets(self, request, obj = ...):
        base_fieldsets = list(super().get_fieldsets(request, obj))

        new_fieldsets = [
            (
                "Basic",
                {
                    'fields': ('cnpj', 'nome_fantasia', 'razao_social')
                }
            ),
        ]
        
        return base_fieldsets + new_fieldsets
