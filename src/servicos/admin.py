from django.contrib import admin

from servicos.models import Agendamento

@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_filter = "status", "cliente", "servico", "trabalhador"