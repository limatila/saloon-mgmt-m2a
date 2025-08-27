from django.contrib import admin

from cadastros.empresas.models import Empresa
from core.bases.admin import BaseAssociadoEmpresaAdmin, DateHierarchyAdmin


@admin.register(Empresa)
class EmpresaAdmin(DateHierarchyAdmin):
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
