from core.bases.views import DynamicSubmodulesView


class ServicosSubmodulesView(DynamicSubmodulesView):
    template_name = "servicos/servicos_list.html"

    all_servicos_modules = ["agendamentos", "servicos", ]

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Serviços"
        return contexto