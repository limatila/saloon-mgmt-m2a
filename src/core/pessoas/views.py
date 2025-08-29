from django.shortcuts import render
from core.bases.views import BaseDynamicListView

class PessoasListView(BaseDynamicListView):
    def get_fields_display(self):
        return ['nome', 'cpf', 'imagem', 'telefone', 'endereco', 'data_criado']