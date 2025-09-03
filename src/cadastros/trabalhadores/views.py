from django.views.generic import CreateView
from django.db.models import Count, Q
from django.urls import reverse_lazy

from core.pessoas.views import PessoasListView, PessoasCreateView
from cadastros.trabalhadores.models import Trabalhador
from cadastros.trabalhadores.forms import TrabalhadoresForm


class TrabalhadoresListView(PessoasListView):
    model = Trabalhador

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        queryset = queryset.annotate(
            agendamentos_totais=Count('agendamento'),
            agendamentos_pendentes=Count('agendamento', filter=Q(agendamento__status="PENDENTE"))
        )
        return queryset

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['title'] = "Lista de Trabalhadores"
        return contexto


class TrabalhadorCreateView(PessoasCreateView, CreateView):
    model = Trabalhador
    form_class = TrabalhadoresForm
    success_url = reverse_lazy('cadastros:trabalhadores:list')

    def form_valid(self, form):
        return super().form_valid(form)
