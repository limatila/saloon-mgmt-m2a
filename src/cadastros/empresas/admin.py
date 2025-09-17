from django.contrib import admin

from core.bases.admin import BaseAdmin
from cadastros.empresas.models import Empresa


@admin.register(Empresa)
class EmpresaAdmin(BaseAdmin):
    search_fields = "cnpj", "nome_fantasia", "razao_social"
    search_help_text = "CNPJ, nome fantasia ou razao social..."

    def get_list_display(self, request):
        base_list = list(super().get_list_display(request))

        new_list = ["cnpj", "nome_fantasia", "razao_social", "imagem"]

        return new_list + base_list

    def get_fieldsets(self, request, obj = ...):
        base_fieldsets = list(super().get_fieldsets(request, obj))

        new_fieldsets = [
            (
                "Basic",
                {
                    'fields': ('cnpj', 'nome_fantasia', 'razao_social', )
                }
            ),
            (
                "Additional",
                {
                    'fields': ('user', 'imagem', )
                }
            )
        ]
        
        return base_fieldsets + new_fieldsets


class BaseAssociadoEmpresaAdmin(BaseAdmin):
    raw_id_fields = "empresa", 
    
    def get_list_display(self, request):
        base_list = list(super().get_list_display(request))

        new_list = ["empresa", ]

        return new_list + base_list

    def get_fieldsets(self, request, obj = ...):
        base_fieldsets = list(super().get_fieldsets(request, obj))

        new_fieldsets = [
            (
                "Empresas",
                {
                    'fields': ('empresa', )
                }
            ),
        ]
        
        return base_fieldsets + new_fieldsets
