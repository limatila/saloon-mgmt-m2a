from datetime import timedelta

from django.db.models import Q, Sum
from django.urls import reverse_lazy
from django.utils import timezone

from core.types import QuickActionItem, QuickInfoItem
from cadastros.clientes.models import Cliente
from cadastros.trabalhadores.models import Trabalhador
from servicos.agendamentos.models import Agendamento
from servicos.agendamentos.choices import (
    AGENDAMENTO_STATUS_PENDENTE,
    AGENDAMENTO_STATUS_EXECUTANDO, 
    AGENDAMENTO_STATUS_FINALIZADO
)


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


#* Mixins especializados
class HomeQuickInfoMixin(ViewComQuickInfoMixin):
    DEFAULT_TOLERANCIA_ATENDIMENTOS_SEGUINTES: int = 2

    def _format_brl_currency(self, value: float | int) -> str:
        """Formata um valor numérico para a moeda brasileira (BRL)."""
        return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    def get_novos_clientes_ultimos_dias(self, tolerancia_dias: int = 7) -> str:
        """
        Especialização para menu Home/

        Args:
            tolerancia_dias (int, optional): quantos dias atrás. Default: 7.
        """
        agora = timezone.now()
        start = agora - timedelta(days=tolerancia_dias)
        end = agora
        return f"+{
            Cliente.objects.filter(
                Q(
                    data_criado__gte=start,
                    data_criado__lte=end
                ) & self.escopo_filter
            ).count()
        }"

    def get_faturamento_da_semana(self) -> str:
        hoje = timezone.now()
        start = (hoje - timedelta(days=hoje.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        end = hoje
        total = Agendamento.objects.aggregate(
            sum=Sum(
                'servico__preco',
                filter=Q(
                    data_agendado__gte=start,
                    data_agendado__lte=end,
                    status=AGENDAMENTO_STATUS_FINALIZADO,
                ) & self.escopo_filter
            )
        ).get('sum') or 0

        return self._format_brl_currency(total)

    def get_faturamento_do_mes(self) -> str:
        hoje = timezone.now()
        start = hoje.replace(day=1)
        end = hoje
        total = Agendamento.objects.aggregate(
                sum=Sum('servico__preco', filter=(
                        Q(
                            data_agendado__gte=start,
                            data_agendado__lte=end,
                            status=AGENDAMENTO_STATUS_FINALIZADO
                        ) & self.escopo_filter
                    )
                )
            ).get('sum') or 0
        
        return f"{self._format_brl_currency(total)} no mês"

    def get_atendimentos_proximas_horas(self, tolerancia_horas: int = DEFAULT_TOLERANCIA_ATENDIMENTOS_SEGUINTES) -> str:
        """
        Args:
            horas (int, optional): quantas horas a partir de agora. Default: 1.
        """
        agora = timezone.now()
        start = agora
        end = agora + timedelta(hours=tolerancia_horas)
        return f"{
            Agendamento.objects.filter(
                Q(
                    data_agendado__gte=start,
                    data_agendado__lte=end,
                    status__in=[AGENDAMENTO_STATUS_PENDENTE, AGENDAMENTO_STATUS_EXECUTANDO]
                ) & self.escopo_filter
            ).count()
        }"

    def get_trabalhadores_ocupados_agora(self, tolerancia_minutos: int = 20) -> str:
        """
        Args:
            tolerancia_minutos (int, optional): quantos minutos antes e depois de agora. Default: 20 (min.).
        """
        agora = timezone.now()
        start = agora - timedelta(minutes=tolerancia_minutos)
        end = agora + timedelta(minutes=tolerancia_minutos)
        return f"{
            Trabalhador.objects.filter(
                Q(
                    agendamentos__status=AGENDAMENTO_STATUS_EXECUTANDO,
                    agendamentos__data_agendado__gte=start,
                    agendamentos__data_agendado__lte=end
                ) & self.escopo_filter
            ).distinct().count()
        }"

    def get_porcentagem_trabalhadores_ocupados(self) -> str:
        total_ocupados_str = self.get_trabalhadores_ocupados_agora()
        total_ocupados = int(total_ocupados_str) if total_ocupados_str.isdigit() else 0
        total_trabalhadores = Trabalhador.objects.filter(
            self.escopo_filter
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
                'conclusion': f'de um total de {Cliente.objects.filter(self.escopo_filter).count()} atuais',
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
                'header': 'Novo Agendamento',
                'description': 'Adicione um registro',
                'fa_icon': 'calendar',
                'link_module': reverse_lazy('servicos:agendamentos:create')
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
