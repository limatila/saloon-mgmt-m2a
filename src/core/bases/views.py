from django.core.exceptions import ImproperlyConfigured
from django.views import View
from django.views.generic import TemplateView
from django.views.generic import ListView, FormView#, CreateView, UpdateView #? DeleteView não recomendado, apenas inativar o registro.
from django.contrib.auth.mixins import LoginRequiredMixin

from core.bases.mixins import EscopoEmpresaQuerysetMixin, EscopoEmpresaFormMixin


class BasePageView(View):
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Base"
        contexto["description"] = "base template"
        contexto["sidebar"] = True
        return contexto


class BaseLoginRequiredView(LoginRequiredMixin, BasePageView):
    pass


# home/
class HomePageView(BaseLoginRequiredView, EscopoEmpresaQuerysetMixin, TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Home"
        contexto["description"] = f"Bem vindo, {self.request.user.first_name or "usuário"}! Aqui está o resumo de {self.request.empresa.nome_fantasia}."
        return contexto


# bases de componentes
class DynamicListView(BaseLoginRequiredView, ListView):
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
        contexto['description'] = f"Veja a listagem de tudo, verifique e modifique os dados que precisar."
        contexto['search'] = self.request.GET.get("search", "")

        return contexto


class DynamicFormView(BaseLoginRequiredView, FormView):
    template_name = "partials/components/form-dashboard.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        nome_formulario_extraido = self.form_class.__name__.replace("Form", ' ').title()
        nome_formulario_extraido = "Serviços" if "tiposervico" in nome_formulario_extraido.lower() else nome_formulario_extraido

        contexto['form_name'] = nome_formulario_extraido
        contexto['title'] = f"Formulário de {contexto['form_name']}"
        contexto['description'] = f"Mude seu registro de {contexto['form_name']}"

        return contexto


class DynamicSubmodulesView(BaseLoginRequiredView, EscopoEmpresaQuerysetMixin, TemplateView):
    """
    Uma view para mostragem de todos os submódulos,
    e links django para eles
    """
    all_cadastros_modules: list[str] = []# = ["clientes", "empresas", "servicos", "trabalhadores"]
    all_servicos_modules: list[str] = []# = ["agendamentos", ]

    def generate_dynamic_urls(self, prefix: str, modules_list: list[str]) -> list[dict[str, str | dict[str, str]]]:    
        if modules_list is None or len(modules_list) == 0:
            return [] #if not defined, return back nothing
        
        modules_list = list(map(lambda module_name: "tipo_servicos" if module_name == "servicos" else module_name, modules_list))
        
        return [
            {
                'name': (
                    module_name.lower()
                        .replace('servicos', 'serviços')
                        .title() 
                        .replace("_", " de ")
                ),
                'url_names': {
                    'Listar': f'{prefix}:{module_name}:list',
                    'Cadastro': f'{prefix}:{module_name}:create',
                    # 'Modificar': f'{prefix}:{module_name}:update',
                    # 'Histórico': f'{prefix}:{module_name}:history'
                    #TODO: finish other view types
                }
            }  
            for module_name in modules_list
        ]


    def get_context_data(self, *args, **kwargs):
        contexto = super().get_context_data(*args, **kwargs)
        contexto["title"] = "Módulos"
        contexto["description"] = f"Escolha o módulo que você quer usar hoje."

        #load modules grid
        contexto['modules'] = (
            self.generate_dynamic_urls('cadastros', self.all_cadastros_modules) +
            self.generate_dynamic_urls('servicos', self.all_servicos_modules)
        )

        return contexto
