import calendar
from datetime import datetime, timedelta

import pydf
from django.template.loader import render_to_string
from django.db.models import Q, Count, Sum

from core.helpers import ConversionHelper
from cadastros.clientes.models import Cliente
from cadastros.trabalhadores.models import Trabalhador
from servicos.agendamentos.models import Agendamento
from servicos.agendamentos.choices import (
    AGENDAMENTO_STATUS_PENDENTE,
    AGENDAMENTO_STATUS_EXECUTANDO,
    AGENDAMENTO_STATUS_FINALIZADO,
    AGENDAMENTO_STATUS_CANCELADO
)


class BaseRelatorio:
    """
    Classe base para a criação de relatórios em PDF.

    Esta classe lida com a inicialização do documento PDF e fornece
    métodos auxiliares que podem ser usados por qualquer relatório.
    """
    template_name: str = None

    def __init__(self, request, ano: int, mes: int):
        if not self.template_name:
            raise ValueError("template_name precisa ser definido.")

        self.request = request
        self.ano = ano
        self.mes = mes
        self.nome = "Relatório Base"
        
        self.mes_referencia = f"{self.mes} / {self.ano}"
        _, ultimo_dia = calendar.monthrange(self.ano, self.mes)
        self.data_inicio = datetime(self.ano, self.mes, 1)
        self.data_fim = datetime(self.ano, self.mes, ultimo_dia).replace(hour=23, minute=59, second=59)

        self.margin_top = 4
        self.margin_right = 5
        self.margin_bottom = 5
        self.margin_left = 4

        self.emissor_nome = (
            self.request.user.get_full_name()
            or self.request.user.username
            or self.request.empresa.nome_fantasia
        )

        #coleta de dados definida para o relatório
        self.coletar_dados()

    def coletar_dados(self):
        """
        Hook principal para coleta de dados a serem inseridos no PDF a ser gerado.
        Ao implementar, atribuir elementos à própria instância de relatório.
        """
        raise NotImplementedError("Subclasses devem implementar o método 'coletar_dados'.")

    def gerar_contexto(self):
        """
        Retorna o contexto que será passado para o template.
        Deve ser implementado para adicionar contextos específicos.
        """
        return {
            "nome": self.nome,
            "mes_referencia": self.mes_referencia,
            "emissor_nome": self.emissor_nome
        }

    def renderizar(self) -> bytes:
        """
        Gera e retorna o documento em string no formato html-string
        """
        return render_to_string(self.template_name, self.gerar_contexto())

    def gerar_pdf(self) -> bytes:
        """
        Entrega o documento em bytes para download.
        """
        html = self.renderizar()
        return pydf.generate_pdf(
                html,
                margin_top=self.margin_top,
                margin_right=self.margin_right,
                margin_bottom=self.margin_bottom,
                margin_left=self.margin_left,
                image_dpi=360,
            )


#* Especializados
class RelatorioAtividadeMensal(BaseRelatorio):
    """
    Gera um relatório de atividade mensal simples.

    Este relatório mostra um resumo do faturamento e do número de atendimentos
    para um determinado mês.
    """
    template_name = "relatorios/mensais/report-mensal-clientes.html"

    def __init__(self, request, ano, mes):
        super().__init__(request, ano, mes)
        self.nome = "Relatório de Atividade Mensal"

    def coletar_dados(self):
        """Busca e calcula os dados necessários no banco de dados."""
        #Agendamentos
        agendamentos_finalizados = Agendamento.objects.filter(
            empresa=self.request.empresa,
            status=AGENDAMENTO_STATUS_FINALIZADO,
            data_agendado__date__gte=self.data_inicio,
            data_agendado__date__lte=self.data_fim
        )
        agendamentos_cancelados = Agendamento.objects.filter(
            empresa=self.request.empresa,
            status=AGENDAMENTO_STATUS_CANCELADO,
            data_agendado__date__gte=self.data_inicio,
            data_agendado__date__lte=self.data_fim
        )
                
        #Agendamentos
        self.faturamento_total_mes = agendamentos_finalizados.aggregate(total=Sum('servico__preco'))['total'] or 0.0
        self.total_agendamentos_finalizados = agendamentos_finalizados.count()
        self.faturamento_total_cancelado = agendamentos_cancelados.aggregate(total=Sum('servico__preco'))['total'] or 0.0
        self.total_agendamentos_cancelados = agendamentos_cancelados.count()


        #Trabalhadores
        trabalhadores_atividade = (
            Trabalhador.objects.filter(
                empresa=self.request.empresa,
                agendamentos__data_agendado__date__gte=self.data_inicio,
                agendamentos__data_agendado__date__lte=self.data_fim
            )
            .values("id", "nome")
            .annotate(
                total_finalizados=Count(
                    "agendamentos", filter=Q(agendamentos__status=AGENDAMENTO_STATUS_FINALIZADO)
                ),
                total_cancelados=Count(
                    "agendamentos", filter=Q(agendamentos__status=AGENDAMENTO_STATUS_CANCELADO)
                ),
                valor_arrecadado_total=Sum(
                    "agendamentos__servico__preco",
                    filter=Q(agendamentos__status=AGENDAMENTO_STATUS_FINALIZADO)
                ),
            )
        )

        self.trabalhadores_mais_agendamentos_finalizados = sorted(
            trabalhadores_atividade, key=lambda x: x["total_finalizados"], reverse=True
        )[:3]

        self.trabalhadores_mais_agendamentos_cancelados = sorted(
            trabalhadores_atividade, key=lambda x: x["total_cancelados"], reverse=True
        )[:3]

        self.trabalhadores_maior_faturamento_total = sorted(
            trabalhadores_atividade, key=lambda x: x["valor_arrecadado_total"] or 0, reverse=True
        )[:3]
    
    def gerar_contexto(self):
        contexto = super().gerar_contexto()

        adicao = {
            "faturamento_total_mes": ConversionHelper.formatar_moeda(self.faturamento_total_mes),
            "total_agendamentos_finalizados": self.total_agendamentos_finalizados,
            "faturamento_total_cancelado": ConversionHelper.formatar_moeda(self.faturamento_total_cancelado),
            "total_agendamentos_cancelados": self.total_agendamentos_cancelados,
            "trabalhadores_mais_agendamentos_finalizados": self.trabalhadores_mais_agendamentos_finalizados,
            "trabalhadores_mais_agendamentos_cancelados": self.trabalhadores_mais_agendamentos_cancelados,
            "trabalhadores_maior_faturamento_total": self.trabalhadores_maior_faturamento_total,
        }

        contexto.update(adicao)
        return contexto


class RelatorioClientesMensal(BaseRelatorio):
    template_name = "relatorios/mensais/report-mensal-atividade.html"

    def __init__(self, request, ano, mes):
        super().__init__(request, ano, mes)
        self.nome = "Relatório de Clientes Mensal"

    def coletar_dados(self):
        #* Clientes Atuais
        self.total_clientes_novos = (
            Cliente.objects.filter(
                    empresa=self.request.empresa,
                    data_criado__gte=self.data_inicio,
                    data_criado__lte=self.data_fim
                )
        ).count()

        clientes_atividades = (
            Cliente.objects.filter(
                empresa=self.request.empresa,
                agendamentos__data_agendado__gte=self.data_inicio,
                agendamentos__data_agendado__lte=self.data_fim
            )
            .values("id", "nome")
            .annotate(
                total_marcados=Count("agendamentos"),
                total_finalizados=Count(
                    "agendamentos", filter=Q(agendamentos__status=AGENDAMENTO_STATUS_FINALIZADO)
                ),
                total_cancelados=Count(
                    "agendamentos", filter=Q(agendamentos__status=AGENDAMENTO_STATUS_CANCELADO)
                ),
            )
        )

        #quais clientes com mais atendimentos marcados
        self.clientes_mais_agendamentos_marcados = sorted(
            clientes_atividades, key=lambda x: x["total_marcados"], reverse=True
        )[:3]

        #quais clientes com mais atendimentos finalizados
        self.clientes_mais_agendamentos_finalizados = sorted(
            clientes_atividades, key=lambda x: x["total_finalizados"], reverse=True
        )[:3]

        #quais clientes com mais atendimentos cancelados
        self.clientes_mais_agendamentos_cancelados = sorted(
            clientes_atividades, key=lambda x: x["total_cancelados"], reverse=True
        )[:3]

        #Cliente que gerou maior faturamento
        self.cliente_maior_faturamento_total = (
            Cliente.objects.filter(empresa=self.request.empresa)
            .annotate(faturamento_total=Sum("agendamentos__servico__preco", filter=Q(agendamentos__status=AGENDAMENTO_STATUS_FINALIZADO)))
            .order_by("-faturamento_total")
            .first()
        )


        #* Clientes recorrentes
        self.total_clientes_unicos = Cliente.objects.filter(
            empresa=self.request.empresa,
            agendamentos__data_agendado__gte=self.data_inicio,
            agendamentos__data_agendado__lte=self.data_fim,
        ).distinct().count() # type: ignore

        self.clientes_recorrentes = (
            Cliente.objects.filter(
                empresa=self.request.empresa,
                agendamentos__data_agendado__gte=self.data_inicio,
                agendamentos__data_agendado__lte=self.data_fim
            )
            .values("id", "nome", "telefone")
            .annotate(
                total_agendamentos=Count("agendamentos", 
                    filter=Q(agendamentos__status__in=[
                        AGENDAMENTO_STATUS_PENDENTE,
                        AGENDAMENTO_STATUS_EXECUTANDO, 
                        AGENDAMENTO_STATUS_FINALIZADO
                    ])
                )
            ).filter(total_agendamentos__gt=1)
            .order_by('-total_agendamentos') # type: ignore
        )

        # nn%
        try:
            calculo_recorrencia = (self.clientes_recorrentes.count() / self.total_clientes_unicos) * 100
        except ZeroDivisionError:
            calculo_recorrencia = 0
        self.porcentagem_recorrencia = f"{calculo_recorrencia:.2f}%"

        self.top_clientes_recorrentes = sorted(
            self.clientes_recorrentes, key=lambda x: x["total_agendamentos"], reverse=True
        )[:3]

        self.top_clientes_antigos_recorrentes = (
            Cliente.objects.filter(
                empresa=self.request.empresa,
                data_criado__lt=self.data_inicio,
                agendamentos__data_agendado__gte=(self.data_inicio - timedelta(days=30 * 6)), # Últimos 6 meses
                agendamentos__data_agendado__lte=self.data_fim # Até o final do mês atual
            ).annotate(
                total_agendamentos=Count("agendamentos", 
                    filter=Q(agendamentos__status__in=[
                        AGENDAMENTO_STATUS_PENDENTE,
                        AGENDAMENTO_STATUS_EXECUTANDO, 
                        AGENDAMENTO_STATUS_FINALIZADO
                    ]) # Contagem de agendamentos não cancelados
                )
            ).filter(total_agendamentos__gt=1) # Clientes com mais de 1 agendamento no período
            .order_by('-total_agendamentos')
        )[:3]

        
        #* Clientes inativos
        # Clientes que não tiveram agendamentos nos últimos 3 meses
        clientes_inativos = (
            Cliente.objects.filter(
                empresa=self.request.empresa
            )
            .annotate(
                total_agendamentos_periodo=Count(
                    "agendamentos",
                    filter=Q(
                        agendamentos__data_agendado__gte=(self.data_inicio - timedelta(days=30 * 6)), # Últimos 6 meses
                        agendamentos__data_agendado__lte=self.data_fim, # Até o final do mês atual
                    ),
                )
            )
            .filter(total_agendamentos_periodo=0)  # Nenhum agendamento nos últimos 6 meses
            .order_by("-data_criado")
        )
        
        self.total_clientes_inativos = clientes_inativos.count()

        # Entre os inativos, pega os que já foram recorrentes no passado
        self.clientes_inativos_antigos_recorrentes = (
            clientes_inativos.annotate(
                total_agendamentos_geral=Count("agendamentos", 
                    filter=Q(agendamentos__status__in=[
                        AGENDAMENTO_STATUS_PENDENTE,
                        AGENDAMENTO_STATUS_EXECUTANDO,
                        AGENDAMENTO_STATUS_FINALIZADO
                    ])
                ) # Contagem de agendamentos não cancelados
            ).filter(
                total_agendamentos_geral__gt=1
            ).order_by("-data_criado")
        )[:3]

    def gerar_contexto(self):
        contexto = super().gerar_contexto()

        adicao = {
            "total_clientes_novos": self.total_clientes_novos,
            "clientes_mais_agendamentos_marcados": self.clientes_mais_agendamentos_marcados,
            "clientes_mais_agendamentos_finalizados": self.clientes_mais_agendamentos_finalizados,
            "clientes_mais_agendamentos_cancelados": self.clientes_mais_agendamentos_cancelados,
            "cliente_maior_faturamento_total": self.cliente_maior_faturamento_total,
            "total_clientes_unicos": self.total_clientes_unicos,
            "porcentagem_recorrencia": self.porcentagem_recorrencia,
            "top_clientes_recorrentes": self.top_clientes_recorrentes,
            "top_clientes_antigos_recorrentes": self.top_clientes_antigos_recorrentes,
            "total_clientes_inativos": self.total_clientes_inativos,
            "clientes_inativos_antigos_recorrentes": self.clientes_inativos_antigos_recorrentes,
        }

        contexto.update(adicao)
        return contexto