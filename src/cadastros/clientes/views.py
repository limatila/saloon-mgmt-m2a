from core.pessoas.views import PessoasListView
from cadastros.clientes.models import Cliente

class ClientesListView(PessoasListView):
    model = Cliente

    def get_context_data(self, *args, **kwargs):
        contexto = super().get_context_data(*args, **kwargs)
        contexto['title'] = "Lista de Clientes"
        return contexto
