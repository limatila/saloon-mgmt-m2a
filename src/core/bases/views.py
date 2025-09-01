from django.core.exceptions import ImproperlyConfigured
# from django.views import View
from django.views.generic import TemplateView, RedirectView
from django.views.generic import ListView#, CreateView, UpdateView #? DeleteView não recomendado, apenas inativar o registro.
from django.contrib.auth.mixins import LoginRequiredMixin

from core.bases.utils.context_generators import generate_dynamic_urls


class BasePageView(LoginRequiredMixin, TemplateView):
    template_name = "base.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Base"
        contexto["sidebar"] = True
        return contexto


class HomePageView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"
    all_cadastros_modules: list[str] = ["clientes", "empresas", "servicos", "trabalhadores"]
    all_servicos_modules: list[str] = ["agendamentos", ]

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Home"

        #load modules grid
        contexto['modules'] = (
            generate_dynamic_urls('cadastros', self.all_cadastros_modules) +
            generate_dynamic_urls('servicos', self.all_servicos_modules) +
            []
        )

        return contexto


# bases de componentes
class BaseDynamicListView(LoginRequiredMixin, ListView):
    """
    Uma view para iterar sobre campos de objetos.
    var 'model' deve ser definido.
    método 'get_field_order' deve ser definido.
    """
    def get_fields_display(self):
        """
        Hook para definir fields_ordenados
        """
        raise ImproperlyConfigured(
            f"{self.__class__.__name__} deve implementar get_field_order(), retornando uma list[str]."
        )

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)

        field_order = self.get_fields_display()

        # Optional: Validate fields exist
        for field in field_order:
            try:
                self.model._meta.get_field(field)
            except Exception:
                raise ImproperlyConfigured(f"'{field}' não é um field de {self.model.__name__}")

        contexto['field_names'] = [
            self.model._meta.get_field(field).verbose_name
            for field in field_order
        ]
        contexto['object_dicts'] = [
            {
                field: getattr(obj, f"get_{field}_display")()
                if callable(getattr(obj, f"get_{field}_display", None))
                else getattr(obj, field)
                for field in field_order
            }
            for obj in contexto['object_list']
        ]
        contexto["sidebar"] = True

        return contexto
