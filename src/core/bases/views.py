from django.core.exceptions import ImproperlyConfigured
from django.urls import NoReverseMatch, reverse
from django.views.generic import TemplateView
from django.views.generic import ListView, FormView#, CreateView, UpdateView #? DeleteView não recomendado, apenas inativar o registro.
from django.contrib.auth.mixins import LoginRequiredMixin

from cadastros.empresas.mixins import EscopoEmpresaQuerysetMixin


#* Base views -- que podem devem ser herdadas por views especializadas
class BasePageView(TemplateView):
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Base"
        contexto["description"] = "base template"
        contexto["sidebar"] = True
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

    def get_create_form_app_name_and_url(self) -> tuple[str]:
        """
        Retorna a URL de criação padrão para este model.
        Padrão de nomeação: '<app_label>:<model_name_lower>:create'
        """
        #conseguindo nomes
        module_name = self.model.module_label #clientes, tipo_servicos
        app_name = self.model._meta.model_name

        plural_names_end_in_es = ["trabalhador"] #add here in singular!

        if app_name:
            #tratamento
            app_name_plural = app_name + "s" if app_name not in plural_names_end_in_es else app_name + "es"
        
            if app_name_plural == "tiposervicos":
                app_name_plural = "tipo_servicos"
            
            #extração
            try:
                url = reverse(f"{module_name}:{app_name_plural}:create")
            except NoReverseMatch:
                url = "" #avoid bugs

            app_name_plural = app_name_plural.replace('_', ' de ').replace('servicos', 'serviços').title()

            return (app_name_plural, url)
        

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

        # em caso de empty
        if self.get_queryset().count() == 0:
            contexto['app_name'], contexto['url_submodule_create'] = self.get_create_form_app_name_and_url()
            

        contexto['description'] = f"Veja a listagem de tudo, verifique e modifique os dados que precisar."
        contexto['search'] = self.request.GET.get("search", "")
        contexto["sidebar"] = True

        return contexto


class BaseDynamicFormView(FormView):
    template_name = "partials/components/form-dashboard.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        nome_formulario_extraido = self.form_class.__name__.replace("Form", ' ').title()
        nome_formulario_extraido = "Serviços" if "tiposervico" in nome_formulario_extraido.lower() else nome_formulario_extraido

        contexto['form_name'] = nome_formulario_extraido
        contexto['title'] = f"Formulário de {contexto['form_name']}"
        contexto['description'] = f"Mude seu registro de {contexto['form_name']}"
        contexto["sidebar"] = True

        return contexto


#* Especializadas: home/ [nome_modulo]/
class HomePageView(LoginRequiredMixin, EscopoEmpresaQuerysetMixin, BasePageView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Home"
        contexto["description"] = f"Bem vindo, {self.request.user.first_name or "usuário"}! Aqui está o resumo de {self.request.empresa.nome_fantasia}."
        return contexto


class DynamicSubmodulesView(LoginRequiredMixin, EscopoEmpresaQuerysetMixin, BasePageView):
    """
    Uma view para mostragem de todos os submódulos,
    e links da url config para eles
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
