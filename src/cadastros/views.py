from django.shortcuts import render

from core.bases.views import BaseDynamicSubmodulesView


class CadastrosSubmodulesView(BaseDynamicSubmodulesView):
    template_name = "cadastros/cadastros_list.html"

    all_cadastros_modules = ["clientes", "empresas", "trabalhadores"]

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Cadastros"
        return contexto
