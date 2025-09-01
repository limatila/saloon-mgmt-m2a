from core.bases.views import BaseDynamicListView

from servicos.agendamentos.models import Agendamento


class AgendamentoListView(BaseDynamicListView):
    model = Agendamento

    def get_fields_display(self):
        return ['data_agendado', 'status', 'cliente', 'servico', 'trabalhador']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Lista de Agendamentos"
        return context
