from django.views.generic import CreateView

from core.bases.views import DynamicListView, DynamicFormView


class PessoasListView(DynamicListView):
    def get_fields_display(self):
        return ['nome', 'cpf', 'imagem', 'telefone', 'endereco']


class PessoasCreateView(DynamicFormView, CreateView):
    pass
