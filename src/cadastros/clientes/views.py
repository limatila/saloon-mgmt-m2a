from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from core.pessoas.views import PessoasListView, PessoasCreateView, PessoasDeleteView
from core.bases.mixins import AtivosQuerysetMixin
from cadastros.empresas.mixins import EscopoEmpresaQuerysetMixin, EscopoEmpresaFormMixin
from cadastros.clientes.models import Cliente
from cadastros.clientes.forms import ClientesForm


class ClientesListView(LoginRequiredMixin, EscopoEmpresaQuerysetMixin, AtivosQuerysetMixin, PessoasListView):
    model = Cliente

    def get_context_data(self, *args, **kwargs):
        contexto = super().get_context_data(*args, **kwargs)
        contexto['title'] = "Lista de Clientes"
        return contexto


class ClienteCreateView(LoginRequiredMixin, EscopoEmpresaFormMixin, PessoasCreateView):
    model = Cliente
    form_class = ClientesForm
    success_url = reverse_lazy('cadastros:clientes:list')

    def form_valid(self, form):
        messages.success(self.request, "✅ Cliente criado com sucesso!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "⚠️ Não foi possível registrar o Cliente!")
        return super().form_invalid(form)


class ClienteDeleteView(LoginRequiredMixin, EscopoEmpresaQuerysetMixin, PessoasDeleteView):
    model = Cliente
    success_url = reverse_lazy('cadastros:clientes:list')