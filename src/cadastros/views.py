from core.bases.views import DynamicSubmodulesView


class CadastrosSubmodulesView(DynamicSubmodulesView):
    template_name = "cadastros/cadastros_list.html"

    all_cadastros_modules = ["clientes", "trabalhadores"]

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Cadastros"
        return contexto
