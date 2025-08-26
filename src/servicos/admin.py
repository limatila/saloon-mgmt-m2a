from django.contrib import admin

from servicos.models import Agendamento

@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_filter = "status", 
    raw_id_fields = "cliente", "servico", "trabalhador"