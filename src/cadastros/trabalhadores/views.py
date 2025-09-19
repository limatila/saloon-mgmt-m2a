from django.db.models import Count, Q
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from core.pessoas.views import PessoasListView, PessoasCreateView, PessoasDeleteView
from core.bases.mixins import AtivosQuerysetMixin, RedirecionarOrigemMixin
from servicos.agendamentos.choices import AGENDAMENTO_STATUS_PENDENTE, AGENDAMENTO_STATUS_FINALIZADO
from cadastros.empresas.mixins import EscopoEmpresaQuerysetMixin, EscopoEmpresaFormMixin
from cadastros.trabalhadores.models import Trabalhador
from cadastros.trabalhadores.forms import TrabalhadoresForm


class TrabalhadoresListView(LoginRequiredMixin, EscopoEmpresaQuerysetMixin, AtivosQuerysetMixin, PessoasListView):
    model = Trabalhador

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        queryset = queryset.annotate(
            agendamentos_totais_finalizados=Count('agendamentos', filter=Q(agendamentos__status=AGENDAMENTO_STATUS_FINALIZADO)),
            agendamentos_pendentes=Count('agendamentos', filter=Q(agendamentos__status=AGENDAMENTO_STATUS_PENDENTE))
        )
        return queryset

    def get_fields_display(self):
        fields_ordernados = super().get_fields_display()
        fields_ordernados += ['agendamentos_totais_finalizados', 'agendamentos_pendentes']
        return fields_ordernados

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['title'] = "Lista de Trabalhadores"
        return contexto


class TrabalhadorCreateView(LoginRequiredMixin, EscopoEmpresaFormMixin, RedirecionarOrigemMixin, PessoasCreateView):
    model = Trabalhador
    form_class = TrabalhadoresForm
    success_url = reverse_lazy('cadastros:trabalhadores:list')

    def form_valid(self, form):
        messages.success(self.request, "✅ Trabalhador criado com sucesso!")  
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "⚠️ Não foi possível registrar o Trabalhador!")  
        return super().form_invalid(form)


class TrabalhadorDeleteView(LoginRequiredMixin, EscopoEmpresaQuerysetMixin, RedirecionarOrigemMixin, PessoasDeleteView):
    model = Trabalhador
    success_url = reverse_lazy('cadastros:trabalhadores:list')