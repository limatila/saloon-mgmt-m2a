from django.core.exceptions import ImproperlyConfigured
from django.views.generic import TemplateView, ListView, FormView, UpdateView #, CreateView, UpdateView #? DeleteView não recomendado, apenas inativar o registro.
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import NoReverseMatch, reverse
from django.conf import settings
from django.shortcuts import redirect
from django.contrib import messages

from core.bases.mixins import DateSearchMixin, HomeQuickInfoMixin, HomeQuickActionMixin, ViewComWorkerStatusMixin
from cadastros.empresas.models import Empresa
from cadastros.empresas.mixins import EscopoEmpresaQuerysetMixin


#* Base views -- que podem devem ser herdadas por views especializadas
class BasePageView(TemplateView):
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["project_title"] = settings.PROJECT_TITLE
        contexto["title"] = "Base"
        contexto["description"] = "base template"
        contexto["sidebar"] = True
        return contexto


# bases de componentes
class BaseDynamicListView(DateSearchMixin, ListView):
    """
    Uma view para iterar sobre campos de objetos.
    var 'model' deve ser definido.
    método 'get_field_order' deve ser definido.
    """
    def get_queryset(self):
        return super().get_queryset().order_by("-data_criado")

    def get_fields_display(self):
        """
        Hook para definir fields_ordenados
        """
        raise ImproperlyConfigured(
            f"{self.__class__.__name__} deve implementar {self.get_fields_display.__name__}(), retornando uma list[str]."
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
        
    def create_object_dict_for_display(self, obj: object, fields: list[str], getter: list) -> dict:
        """Cria um dicionário para um único objeto usando os acessadores pré-calculados."""
        object_dict = {
            field: accessor(obj)
            for field, accessor in zip(fields, getter)
        }
        object_dict['pk'] = obj.pk  # certifique-se que pk está incluído
        return object_dict

    def get_context_data(self, **kwargs):
        def get_verbose_name(field_name):
            """Obtém o verbose_name de um campo do modelo ou retorna o nome do campo."""
            try:
                return self.model._meta.get_field(field_name).verbose_name
            except Exception:
                # O campo pode ser uma anotação (annotation) ou propriedade, que não está em _meta.
                # Retorna o nome do campo formatado.
                return field_name.replace('_', ' ').title()
        

        contexto = super().get_context_data(**kwargs)

        field_order = self.get_fields_display()

        # Adiciona os campos anotados aos nomes de exibição
        # (A validação anterior foi removida para permitir campos anotados)
        contexto['field_names'] = [
            get_verbose_name(field) for field in field_order
        ]


        # Otimização: Em vez de verificar a existência de 'get_..._display' para cada célula,
        # criamos uma lista de "getters" uma vez e a reutilizamos para cada objeto.
        fields_getters = []
        for field in field_order:
            # Tenta obter o método get_<field>_display
            display_method = getattr(self.model, f"get_{field}_display", None)
            if callable(display_method):
                # Se o método existir no modelo (ex: de um choices), usa ele.
                # Usamos uma lambda para capturar o 'field' e aplicá-lo ao objeto na iteração.
                fields_getters.append(lambda obj, f=field: getattr(obj, f"get_{f}_display")())
            else:
                # Caso contrário, acessa o atributo diretamente.
                fields_getters.append(lambda obj, f=field: getattr(obj, f))


        contexto['object_dicts'] = [
            self.create_object_dict_for_display(obj, field_order, fields_getters)
            for obj in contexto['object_list']
        ]

        if not self.model is Empresa:
            contexto['app_name'], contexto['url_submodule_create'] = self.get_create_form_app_name_and_url()

        contexto["project_title"] = settings.PROJECT_TITLE
        contexto['description'] = f"Veja a listagem de tudo, verifique e modifique os dados que precisar."
        contexto['search'] = self.request.GET.get("search", "")
        contexto['data_search_name'] = "de Criação"
        contexto["sidebar"] = True

        return contexto


class BaseDynamicFormView(FormView):
    template_name = "partials/components/dashboards/form-dashboard.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)

        nome_formulario_extraido = self.form_class.__name__.replace("Form", ' ').title()
        nome_formulario_extraido = "Serviços" if "tiposervico" in nome_formulario_extraido.lower() else nome_formulario_extraido

        contexto['form_name'] = nome_formulario_extraido
        contexto['title'] = f"Formulário de {contexto['form_name']}"
        contexto['description'] = f"Mude seu registro de {contexto['form_name']}"
        contexto["sidebar"] = True

        return contexto


# class BaseCreateFormView

class BaseDeleteView(UpdateView):
    template_name = "partials/components/dashboards/form-dashboard.html"
    fields = ['ativo']

    def get_object(self, queryset = None):
        obj = super().get_object(queryset)
        if obj.empresa != self.request.empresa:
            messages.error(self.request, "⚠️ Você não tem permissão para editar este objeto.")
            redirect(self.request.path)
        return obj

    def post(self, request, *args, **kwargs):
        obj = self.get_object()

        if obj.ativo:
            obj.ativo = False
            obj.save()
            messages.success(self.request, f"✅ {self.model._meta.verbose_name.title()} deletado com sucesso!")
        else:
            messages.error(self.request, f"⛔ O {self.model._meta.verbose_name.title()} já está deletado!")

        return redirect(self.success_url or 'home')


#* Especializadas: home/ [nome_modulo]/
class HomePageView(LoginRequiredMixin, EscopoEmpresaQuerysetMixin, HomeQuickInfoMixin, HomeQuickActionMixin, ViewComWorkerStatusMixin, BasePageView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Ínicio"
        contexto["description"] = f"Bem vindo, {self.request.user.first_name or 'usuário'}! Aqui está o resumo de <b>{self.request.empresa.nome_fantasia}</b>."
        return contexto


class DynamicSubmodulesView(LoginRequiredMixin, EscopoEmpresaQuerysetMixin, BasePageView):
    """
    Uma view para mostragem de todos os submódulos,
    e links da url config para eles
    """
    all_cadastros_modules: list[str] = []# = ["clientes", "empresas",  "trabalhadores"]
    all_servicos_modules: list[str] = []# = ["agendamentos", "servicos" ]

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


class SelecaoDynamicListView(BaseDynamicListView):
    template_name = "selection-menu.html"

    def get_selecao_or_redirect(self, request) -> str:
        selecao_id = request.POST.get("selecao_id")
        if not selecao_id:
            redirect(self.request.path)

        return selecao_id
