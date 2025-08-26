from django.contrib import admin

from core.admin import DateHierarchyAdmin
from servicos.models import Agendamento

@admin.register(Agendamento)
class AgendamentoAdmin(DateHierarchyAdmin):
    list_filter = "status", 
    raw_id_fields = "cliente", "servico", "trabalhador"