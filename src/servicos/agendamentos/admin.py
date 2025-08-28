from django.contrib import admin

from core.bases.admin import BaseAssociadoEmpresaAdmin, DateHierarchyAdmin
from servicos.agendamentos.models import Agendamento

@admin.register(Agendamento)
class AgendamentoAdmin(
        DateHierarchyAdmin, 
        BaseAssociadoEmpresaAdmin
    ):
    list_filter = "status", 
    raw_id_fields = "cliente", "servico", "trabalhador", "empresa"
    search_fields = "status", #! is getting only by enum values, not get_display
    search_help_text = "Status..."

    def get_list_display(self, request):
        base_list = list(super().get_list_display(request))

        new_list = ["data_agendado", "cliente", "servico", "trabalhador"]

        return new_list + base_list

    def get_list_display_links(self, request, list_display):
        base_list = list(super().get_list_display(request))

        new_list = ["cliente", "servico", "trabalhador" ]

        return new_list + base_list

    def get_fieldsets(self, request, obj = ...):
        base_fieldsets = list(super().get_fieldsets(request, obj))

        new_fieldsets = [
            (
                "Basic",
                {
                    'fields': ('data_agendado', 'cliente', 'servico', 'trabalhador')
                }
            ),
            (
                "Additional",
                {
                    'fields': ('status', )
                }
            )
        ]
        
        return base_fieldsets + new_fieldsets