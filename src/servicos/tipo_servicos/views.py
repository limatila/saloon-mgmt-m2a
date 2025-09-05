from django.views.generic import CreateView
from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin
from core.bases.views import BaseDynamicListView, BaseDynamicFormView
from cadastros.empresas.mixins import EscopoEmpresaQuerysetMixin, EscopoEmpresaFormMixin
from servicos.tipo_servicos.models import TipoServico
from servicos.tipo_servicos.forms import TipoServicoForm


class TipoServicoListView(LoginRequiredMixin, EscopoEmpresaQuerysetMixin, BaseDynamicListView):
    model = TipoServico

    def get_fields_display(self):
        return ['nome', 'preco']

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['title'] = "Lista de Serviços"
        return contexto


class TipoServicoCreateView(LoginRequiredMixin, EscopoEmpresaFormMixin, BaseDynamicFormView, CreateView):
    model = TipoServico
    form_class = TipoServicoForm
    success_url = reverse_lazy('cadastros:tipo_servicos:list')

    def form_valid(self, form):
        return super().form_valid(form)
