from django.views.generic import CreateView

from core.bases.views import BaseDynamicListView, BaseDynamicFormView


class PessoasListView(BaseDynamicListView):
    def get_fields_display(self):
        return ['nome', 'cpf', 'imagem', 'telefone', 'endereco']


class PessoasCreateView(BaseDynamicFormView, CreateView):
    pass
