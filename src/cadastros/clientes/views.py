from django.urls import reverse_lazy

from django.contrib.auth.mixins import LoginRequiredMixin
from core.pessoas.views import PessoasListView, PessoasCreateView
from cadastros.empresas.mixins import EscopoEmpresaQuerysetMixin, EscopoEmpresaFormMixin
from cadastros.clientes.models import Cliente
from cadastros.clientes.forms import ClientesForm


class ClientesListView(LoginRequiredMixin, EscopoEmpresaQuerysetMixin, PessoasListView):
    model = Cliente

    def get_context_data(self, *args, **kwargs):
        contexto = super().get_context_data(*args, **kwargs)
        contexto['title'] = "Lista de Clientes"
        return contexto


class ClienteCreateView(LoginRequiredMixin, EscopoEmpresaFormMixin, PessoasCreateView):
    model = Cliente
    form_class = ClientesForm
    success_url = reverse_lazy('cadastros:clientes:list')
    