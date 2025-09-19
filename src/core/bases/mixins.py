from datetime import date, datetime, timedelta 

from django.db.models import Q, Sum, OuterRef, Subquery
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from core.helpers import ConversionHelper
from core.types import QuickActionItem, QuickInfoItem, TableOptionItemModal
from cadastros.clientes.models import Cliente
from cadastros.trabalhadores.models import Trabalhador
from servicos.agendamentos.models import Agendamento
from servicos.agendamentos.choices import (
    AGENDAMENTO_STATUS_PENDENTE,
    AGENDAMENTO_STATUS_EXECUTANDO, 
    AGENDAMENTO_STATUS_FINALIZADO
)


class AtivosQuerysetMixin:
    @property
    def ativos_filter(self):
        return Q(ativo=True)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(self.ativos_filter)
        return queryset


class FormComArquivoMixin:
    """
    Inclui também os arquivos (FILES) no form.
    """
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['form_with_file'] = True
        return contexto

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            "files": self.request.FILES or None
        })
        return kwargs


class RedirecionarOrigemMixin:
    """
    Mixin para redirecionar para a URL de origem (next) após o sucesso do form / view.
    """
    redirect_field_name = "next"
    success_url = "/" #default, sobescrevível

    def get_success_url(self):
        next_url = (
            self.request.GET.get(self.redirect_field_name)
            or self.request.POST.get(self.redirect_field_name)
        )

        # valida se é seguro
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={self.request.get_host()}):
            return next_url
        else:
            return str(self.success_url)


class DateSearchMixin:
    def get_query_range_dates(self) -> tuple:
        data_1 = self.request.GET.get("data_1")
        data_2 = self.request.GET.get("data_2")
        return (data_1, data_2)

    def get_queryset(self):
        queryset = super().get_queryset()

        data_inicio, data_fim = self.get_query_range_dates()
        if data_inicio:
            queryset = queryset.filter(
                data_criado__gte=data_inicio
            )
        if data_fim:
            queryset = queryset.filter(
                data_criado__lte=data_fim
            )

        return queryset


#* Para exibições de dashboards padrões
class ViewComQuickInfoMixin:
    def get_item_querys(self) -> list[dict[str, str]]:
        """
        Hook para definição de querys dos itens de quick info

        * Formato necessário:
        
            {
                'header': '...',
                'value': '[valor/query]',
                'conclusion': '[valor/query]',
                'fa_icon': '[classe FontAwesome, sem 'fa-']',
                'link_module: 'reverse_lazy('caminho:pelo:namespace')'
            }
        """
        return [
            {
                'header': None,
                'value': None,
                'conclusion': None,
                'fa_icon': None,
                'link_module': None
            }
        ]

    def get_quick_infos(self, max_items: int = 4) -> list:
        return [
            QuickInfoItem(
                header=info.get('header'),
                value=info.get('value'),
                conclusion=info.get('conclusion'),
                fa_icon=info.get('fa_icon'),
                link_module=info.get('link_module')
            )
            for info in self.get_item_querys()[:max_items]
        ]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quick_infos'] = self.get_quick_infos()
        return context


class ViewComQuickActionMixin:
    def get_item_actions(self) -> list[dict[str, str]]:
        """
        Hook para definição de querys dos itens de quick actions

        * Formato necessário:
        
            {
                'header': '...',
                'description': '...',
                'fa_icon': 'classe FontAwesome, sem 'fa-''
                'link_module: 'reverse_lazy('caminho:pelo:namespace')'
            }
        """
        return [
            {
                'header': None,
                'description': None,
                'fa_icon': None,
                'link_module': None
            }
        ]

    def get_quick_actions(self, max_items: int | None = 4) -> list:
        return [
            QuickActionItem(
                header=info.get('header'),
                description=info.get('description'),
                fa_icon=info.get('fa_icon'),
                link_module=info.get('link_module')
            )
            for info in self.get_item_actions()[:max_items]
        ]   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['quick_actions'] = self.get_quick_actions()
        return context


class ViewComWorkerStatusMixin:
    def get_trabalhadores_status(self, limit: int = 20) -> list[dict]:
        agora = timezone.now()
        start = agora - timedelta(hours=1)
        end = agora + timedelta(hours=1)

        # Subquery: último agendamento agendado na última hora
        ultimos_agendamentos_datas = Subquery(
            Agendamento.objects.filter(
                empresa=self.request.empresa,
                trabalhador=OuterRef('pk'),
                status=AGENDAMENTO_STATUS_EXECUTANDO,
                data_agendado__gte=start,
                data_agendado__lte=end
            )
            .order_by('-data_agendado')
            .values('data_agendado')[:1]
        )

        # Trabalhadores anotados com a data do último agendamento agendado na última hora
        queryset = (
            Trabalhador.objects.filter(empresa=self.request.empresa)
            .annotate(ultimo_agendamento_data=ultimos_agendamentos_datas)
            .values('id', 'nome', 'telefone', 'ultimo_agendamento_data')
            .order_by('ultimo_agendamento_data')[:limit]
        )

        return list(queryset)

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)

        trabalhadores_status_list = self.get_trabalhadores_status()
        for trabalhador in trabalhadores_status_list:
            # Se tiver agendamento agendado na última hora → ocupado
            trabalhador['status'] = "ocupado" if trabalhador['ultimo_agendamento_data'] else "disponível"

        contexto['trabalhadores_status_list'] = trabalhadores_status_list
        return contexto


class BaseViewComTableOptionsMixin:
    def get_options_modal(self) -> list[dict[str, str]]:
        """
        Hook para definição de querys dos itens de quick actions

        * Formato necessário:
        
            {
                'nome': '...',
                'description': '...',
                'fa_icon': 'classe FontAwesome, sem 'fa-''
                'link_module: 'reverse_lazy('caminho:pelo:namespace')'
            }
        """
        return [
            {
                'nome': None,
                'description': None,
                'fa_icon': None,
                'link_module': None
            }
        ]

    def get_item_options_for_obj(self, obj) -> list[TableOptionItemModal]:
        """
        Generate item options with TableOptionItemModal for a single object, injecting the pk.
        """
        actions = []
        for blueprint in self.get_item_options_blueprint():
            reverse_name = blueprint.get("reverse_name")
            # reverse the URL with obj.pk
            if reverse_name:
                link = reverse_lazy(reverse_name, args=[obj.pk])
            else:
                link = None
            actions.append(
                TableOptionItemModal(
                    nome=blueprint.get("nome"),
                    description=blueprint.get("description"),
                    fa_icon=blueprint.get("fa_icon"),
                    link_module=link
                )
            )
        return actions

    def get_table_options(self) -> list[list[TableOptionItemModal]]:
        """
        Returns a list of lists: each row in object_list has its own list of actions.
        """
        table_options = []
        for obj in getattr(self, "object_list", []):
            table_options.append(self.get_item_options_for_obj(obj))
        return table_options

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quick_actions"] = self.get_table_options()
        return context


#* Mixins especializados
class HomeQuickInfoMixin(AtivosQuerysetMixin, ViewComQuickInfoMixin):
    DEFAULT_TOLERANCIA_ATENDIMENTOS_SEGUINTES: int = 2

    def get_novos_clientes_ultimos_dias(self, tolerancia_dias: int = 7) -> str:
        """
        Especialização para menu Home/

        Args:
            tolerancia_dias (int, optional): quantos dias atrás. Default: 7.
        """
        hoje = timezone.make_aware(datetime.combine(date.today(), datetime.max.time()))
        start = hoje - timedelta(days=tolerancia_dias)
        end = hoje
        quantidade = Cliente.objects.filter(
            Q(data_criado__gte=start, data_criado__lte=end) & self.empresa_filter & self.ativos_filter
        ).count()

        return f"+{quantidade}"

    def get_faturamento_da_semana(self) -> str:
        hoje = timezone.make_aware(datetime.combine(date.today(), datetime.max.time()))
        start = (hoje - timedelta(days=hoje.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        end = hoje
        total = Agendamento.objects.aggregate(
            sum=Sum(
                'servico__preco',
                filter=Q(
                    data_agendado__gte=start,
                    data_agendado__lte=end,
                    status=AGENDAMENTO_STATUS_FINALIZADO,
                ) & self.empresa_filter & self.ativos_filter
            )
        ).get('sum') or 0

        return ConversionHelper.formatar_moeda(total)

    def get_faturamento_do_mes(self) -> str:
        hoje = timezone.make_aware(datetime.combine(date.today(), datetime.max.time()))
        start = datetime.combine(hoje.replace(day=1), datetime.min.time())
        end = hoje
        total = Agendamento.objects.aggregate(
                sum=Sum('servico__preco', filter=(
                        Q(
                            data_agendado__gte=start,
                            data_agendado__lte=end,
                            status=AGENDAMENTO_STATUS_FINALIZADO
                        ) & self.empresa_filter & self.ativos_filter
                    )
                )
            ).get('sum') or 0
        
        return f"{ConversionHelper.formatar_moeda(total)} no mês"

    def get_atendimentos_proximas_horas(self, tolerancia_horas: int = DEFAULT_TOLERANCIA_ATENDIMENTOS_SEGUINTES) -> str:
        """
        Args:
            horas (int, optional): quantas horas a partir de agora. Default: 1.
        """
        agora = timezone.now()
        start = agora
        end = agora + timedelta(hours=tolerancia_horas)
        
        quantidade = (
            Agendamento.objects.filter(
                Q(
                    data_agendado__gte=start,
                    data_agendado__lte=end,
                    status__in=[AGENDAMENTO_STATUS_PENDENTE, AGENDAMENTO_STATUS_EXECUTANDO]
                ) & self.empresa_filter & self.ativos_filter
            ).count()
        )

        return f"{quantidade}"

    def get_trabalhadores_ocupados_agora(self, tolerancia_minutos: int = 20) -> str:
        """
        Args:
            tolerancia_minutos (int, optional): quantos minutos antes e depois de agora. Default: 20 (min.).
        """
        agora = timezone.now()
        start = agora - timedelta(minutes=tolerancia_minutos)
        end = agora + timedelta(minutes=tolerancia_minutos)
        
        quantidade = (
            Trabalhador.objects.filter(
                Q(
                    agendamentos__status=AGENDAMENTO_STATUS_EXECUTANDO,
                    agendamentos__data_agendado__gte=start,
                    agendamentos__data_agendado__lte=end
                ) & self.empresa_filter & self.ativos_filter
            ).distinct().count()
        )
        
        return f"{quantidade}"

    def get_porcentagem_trabalhadores_ocupados(self) -> str:
        total_ocupados_str = self.get_trabalhadores_ocupados_agora()
        total_ocupados = int(total_ocupados_str) if total_ocupados_str.isdigit() else 0
        total_trabalhadores = Trabalhador.objects.filter(
            self.empresa_filter & self.ativos_filter
        ).count()

        if total_trabalhadores == 0:
            return "0%"
        porcentagem = (total_ocupados / total_trabalhadores) * 100
        return f"{porcentagem:.0f}%"

    def get_item_querys(self):
        tolerancia_novos_clientes = 7

        return [
            {
                'header': 'Clientes novos na semana',
                'value': self.get_novos_clientes_ultimos_dias(tolerancia_novos_clientes),
                'conclusion': f'de um total de {Cliente.objects.filter(self.empresa_filter & self.ativos_filter).count()} atuais',
                'fa_icon': 'user',
                'link_module': reverse_lazy('cadastros:clientes:list')
            },
            {
                'header': 'Faturamento da semana',
                'value': self.get_faturamento_da_semana(),
                'conclusion': self.get_faturamento_do_mes(),
                'fa_icon': 'dollar-sign',
                'link_module': reverse_lazy('servicos:tipo_servicos:list')
            },
            {
                'header': 'Atendimentos a seguir',
                'value': self.get_atendimentos_proximas_horas(),
                'conclusion': f'nas próximas {self.DEFAULT_TOLERANCIA_ATENDIMENTOS_SEGUINTES} horas',
                'fa_icon': 'clock',
                'link_module': reverse_lazy('servicos:agendamentos:list')
            },
            {
                'header': 'Trabalhadores ocupados',
                'value': self.get_trabalhadores_ocupados_agora(),
                'conclusion': f'{self.get_porcentagem_trabalhadores_ocupados()} de todos estão ocupados',
                'fa_icon': 'briefcase',
                'link_module': reverse_lazy('cadastros:trabalhadores:list')
            }
        ]


class HomeQuickActionMixin(ViewComQuickActionMixin):
    def get_item_actions(self):
        return [
            {
                'header': 'Planilha Diária',
                'description': 'Verifique os agendamentos do dia',
                'fa_icon': 'users',
                'link_module': reverse_lazy('servicos:agendamentos:planilha_diaria', args=[0]),
            },
            {
                'header': 'Finalizar Agendamento',
                'description': 'Finalize o atendimento',
                'fa_icon': 'check',
                'link_module': reverse_lazy('servicos:agendamentos:finalizar')
            },
            {
                'header': 'Novo Cliente',
                'description': 'Adicione uma pessoa recorrente',
                'fa_icon': 'circle-user',
                'link_module': reverse_lazy('cadastros:clientes:create')
            },
            {
                'header': 'Novo Serviço',
                'description': 'Adicione um novo procedimento',
                'fa_icon': 'scissors',
                'link_module': reverse_lazy('servicos:tipo_servicos:create')
            },
        ]


# TODO: implement in submodules -------------
# class ModuleQuickInfoMixin(ViewComQuickInfoMixin):
#     def get_item_querys(self):
#         return [
#             {
#                 'header'
#             },
#             {
#                 'header'
#             },
#             {
#                 'header'
#             },
#             {
#                 'header'
#             }
#         ]
