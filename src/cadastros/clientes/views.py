from core.bases.views import DynamicListView

from cadastros.clientes.models import Cliente

class ClientesListView(DynamicListView):
    model = Cliente
    def get_fields_display(self):
        return ['nome', 'cpf', 'imagem', 'telefone', 'endereco', 'data_criado']


    def get_context_data(self, *args, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['title'] = "Lista de Clientes"
        return contexto
