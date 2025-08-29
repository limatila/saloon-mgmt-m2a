from django.views.generic import ListView

from cadastros.clientes.models import Cliente

class ClientesListView(ListView):
    model = Cliente
    

    def get_context_data(self, *args, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['title'] = "Lista de Clientes"
        return contexto
