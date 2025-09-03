from django.urls import reverse_lazy
from django.views.generic import CreateView

from core.bases.views import BaseDynamicListView, BaseDynamicFormView
from servicos.agendamentos.models import Agendamento
from servicos.agendamentos.forms import AgendamentoForm


class AgendamentoListView(BaseDynamicListView):
    model = Agendamento

    def get_fields_display(self):
        return ['data_agendado', 'status', 'cliente', 'servico', 'trabalhador']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Lista de Agendamentos"
        return context


class AgendamentoCreateView(BaseDynamicFormView, CreateView):
    model = Agendamento
    form_class = AgendamentoForm
    success_url = reverse_lazy('servicos:agendamentos:list')

    def form_valid(self, form):
        return super().form_valid(form)
    