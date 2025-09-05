from django.views.generic import CreateView
from django.urls import reverse_lazy

from core.bases.views import DynamicListView, BaseDynamicFormView
from core.bases.mixins import EscopoEmpresaQuerysetMixin, EscopoEmpresaFormMixin
from cadastros.tipo_servicos.models import TipoServico
from cadastros.tipo_servicos.forms import TipoServicoForm


class TipoServicoListView(EscopoEmpresaQuerysetMixin, DynamicListView):
    model = TipoServico

    def get_fields_display(self):
        return ['nome', 'preco']

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['title'] = "Lista de Serviços"
        return contexto


class TipoServicoCreateView(EscopoEmpresaFormMixin, BaseDynamicFormView, CreateView):
    model = TipoServico
    form_class = TipoServicoForm
    success_url = reverse_lazy('cadastros:tipo_servicos:list')

    def form_valid(self, form):
        return super().form_valid(form)
