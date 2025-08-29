from django.core.exceptions import ImproperlyConfigured
from django.views import View
from django.views.generic import TemplateView
from django.views.generic import CreateView, ListView, UpdateView #DeleteView não recomendado, apenas inativar o registro.


class BaseView(TemplateView):
    template_name = "base.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Base"
        contexto["nome"] = "atila"
        return contexto


# bases de componentes
class BaseDynamicListView(ListView):
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
        context = super().get_context_data(**kwargs)

        field_order = self.get_fields_display()

        # Optional: Validate fields exist
        for field in field_order:
            try:
                self.model._meta.get_field(field)
            except Exception:
                raise ImproperlyConfigured(f"'{field}' não é um field de {self.model.__name__}")

        context['field_names'] = [
            self.model._meta.get_field(field).verbose_name
            for field in field_order
        ]
        context['object_dicts'] = [
            {
                field: getattr(obj, f"get_{field}_display")()
                if callable(getattr(obj, f"get_{field}_display", None))
                else getattr(obj, field)
                for field in field_order
            }
            for obj in context['object_list']
        ]

        return context
