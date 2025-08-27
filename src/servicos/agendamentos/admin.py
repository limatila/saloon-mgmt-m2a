from django.contrib import admin

from core.bases.admin import BaseAssociadoEmpresaAdmin, DateHierarchyAdmin
from servicos.agendamentos.models import Agendamento

@admin.register(Agendamento)
class AgendamentoAdmin(DateHierarchyAdmin, BaseAssociadoEmpresaAdmin):
    list_filter = "status", 
    raw_id_fields = "cliente", "servico", "trabalhador"