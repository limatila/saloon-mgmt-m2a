from django.views.generic import CreateView
from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from core.pessoas.views import PessoasListView, PessoasCreateView
from cadastros.empresas.mixins import EscopoEmpresaQuerysetMixin, EscopoEmpresaFormMixin
from cadastros.trabalhadores.models import Trabalhador
from cadastros.trabalhadores.forms import TrabalhadoresForm


class TrabalhadoresListView(LoginRequiredMixin, EscopoEmpresaQuerysetMixin, PessoasListView):
    model = Trabalhador

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        queryset = queryset.annotate(
            agendamentos_totais=Count('agendamentos'),
            agendamentos_pendentes=Count('agendamentos', filter=Q(agendamentos__status="PENDENTE"))
        )
        return queryset

    # TODO: mostrar annotated
    # def get_fields_display(self):
    #     fields_ordernados = super().get_fields_display()
    #     fields_ordernados += ['agendamentos_totais', 'agendamentos_pendentes']
    #     return fields_ordernados

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['title'] = "Lista de Trabalhadores"
        return contexto


class TrabalhadorCreateView(LoginRequiredMixin, EscopoEmpresaFormMixin, PessoasCreateView):
    model = Trabalhador
    form_class = TrabalhadoresForm
    success_url = reverse_lazy('cadastros:trabalhadores:list')

    def form_valid(self, form):
        return super().form_valid(form)
