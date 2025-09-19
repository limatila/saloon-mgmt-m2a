from math import floor
from decimal import Decimal, InvalidOperation

from django.views.generic import CreateView
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin

from core.bases.views import BaseDynamicListView, BaseDynamicFormView, BaseDeleteView
from core.bases.mixins import AtivosQuerysetMixin, RedirecionarOrigemMixin
from cadastros.empresas.mixins import EscopoEmpresaQuerysetMixin, EscopoEmpresaFormMixin
from servicos.tipo_servicos.models import TipoServico
from servicos.tipo_servicos.forms import TipoServicoForm


class TipoServicoListView(LoginRequiredMixin, EscopoEmpresaQuerysetMixin, AtivosQuerysetMixin, BaseDynamicListView):
    model = TipoServico

    def get_fields_display(self):
        return ['nome', 'preco']

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("query", "").strip()

        if query:
            condicao_nome = Q(nome__icontains=query)
            try:
                value = floor(Decimal(query))
                condicao_preco = Q(preco__gte=value, preco__lt=value + 1)
            except InvalidOperation:
                # ignore invalid numbers, leave only name filter
                pass

            queryset = queryset.filter(
                condicao_nome | condicao_preco
            )

        return queryset

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['title'] = "Lista de Serviços"
        return contexto


class TipoServicoCreateView(LoginRequiredMixin, EscopoEmpresaFormMixin, BaseDynamicFormView, RedirecionarOrigemMixin, CreateView):
    model = TipoServico
    form_class = TipoServicoForm
    success_url = reverse_lazy('servicos:tipo_servicos:list')

    def form_valid(self, form):
        messages.success(self.request, "✅ Tipo de serviço criado com sucesso!")  
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "⚠️ Não foi possível criar o Tipo de serviço!")  
        return super().form_invalid(form)


class TipoServicoDeleteView(LoginRequiredMixin, EscopoEmpresaQuerysetMixin, RedirecionarOrigemMixin, BaseDeleteView):
    model = TipoServico
    success_url = reverse_lazy('servicos:tipo_servicos:list')