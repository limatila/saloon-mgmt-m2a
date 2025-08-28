from django.shortcuts import render
from django.views.generic import ListView

from cadastros.clientes.models import Cliente


class ClientesListView(ListView):
    model = Cliente
    template_name = "cliente_list.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['title'] = "Lista de Clientes"
        return contexto
