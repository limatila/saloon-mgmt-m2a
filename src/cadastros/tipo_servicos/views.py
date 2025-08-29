from core.bases.views import BaseDynamicListView
from cadastros.tipo_servicos.models import TipoServico


class TipoServicoListView(BaseDynamicListView):
    model = TipoServico

    def get_fields_display(self):
        return ['nome', 'preco']

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['title'] = "Lista de Serviços"
        return contexto
