from django.urls import reverse_lazy

from core.pessoas.views import PessoasListView, PessoasCreateView
from cadastros.clientes.models import Cliente
from cadastros.clientes.forms import ClientesForm

class ClientesListView(PessoasListView):
    model = Cliente

    def get_context_data(self, *args, **kwargs):
        contexto = super().get_context_data(*args, **kwargs)
        contexto['title'] = "Lista de Clientes"
        return contexto


class ClienteCreateView(PessoasCreateView):
    model = Cliente
    form_class = ClientesForm
    success_url = reverse_lazy('cadastros:clientes:list')

    def form_valid(self, form):
        return super().form_valid(form)
    