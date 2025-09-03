from core.pessoas.views import BaseDynamicListView

from cadastros.empresas.models import Empresa


class EmpresaListView(BaseDynamicListView):
    model = Empresa

    def get_fields_display(self):
        return ['cnpj', 'nome_fantasia', 'razao_social']

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['title'] = "Lista de Empresas"
        return contexto
