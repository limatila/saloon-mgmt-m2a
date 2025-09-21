import calendar
from datetime import datetime, timedelta

from django.db.models import Q, Count, Sum
from django.contrib.staticfiles import finders
import pymupdf

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
from core.bases.mixins import AtivosQuerysetMixin


class BaseRelatorio:
    """
    Classe base para a criação de relatórios em PDF.

    Esta classe lida com a inicialização do documento PDF e fornece
    métodos auxiliares que podem ser usados por qualquer relatório.
    """
    def __init__(self, request, ano: int, mes: int):
        self.request = request
        self.ano = ano
        self.mes = mes
        self.nome = "Relatório Base"
        
        _, ultimo_dia = calendar.monthrange(self.ano, self.mes)
        self.data_inicio = datetime(self.ano, self.mes, 1)
        self.data_fim = datetime(self.ano, self.mes, ultimo_dia).replace(hour=23, minute=59, second=59)

        self.mes_referencia = f"{self.mes} / {self.ano}"
        self.emissor_nome = (
            self.request.user.get_full_name()
            or self.request.user.username
            or self.request.empresa.nome_fantasia
        )
        self.lista_execucao = [] #adicionar aqui todos os métodos representando seções

        # Passo 1: Criar um documento PDF em branco na memória.
        self.doc = pymupdf.open()
        # Passo 2: Adicionar uma página em branco ao documento.
        self.page = self.doc.new_page()
        
        # configs de tamanhos do doc
        self.font_sizes = {
            'title': 14,
            'sub-title': 11,
            'small': 9
        }
        self.ponto_inicial = (50, 72)

        # Passo 3: Carregar e registrar fontes customizadas.
        try:
            # Localiza os arquivos de fonte usando o Django staticfiles finders
            regular_font_path = finders.find('fonts/DejaVuSans.ttf')
            bold_font_path = finders.find('fonts/DejaVuSans-Bold.ttf')

            if not regular_font_path or not bold_font_path:
                raise FileNotFoundError("Fontes customizadas não encontradas via staticfiles finders.")

            # Registra as fontes na página com alias
            self.page.insert_font(fontname="F0-Regular", fontfile=regular_font_path)
            self.page.insert_font(fontname="F1-Bold", fontfile=bold_font_path)

            self.font_regular = "F0-Regular"
            self.font_bold = "F1-Bold"

        except Exception as e:
            print(f"Warning: fontes personalizadas não foram carregadas. Usando fontes padrão do PyMuPDF. Detalhes: {e}")
            # Se não encontrar as fontes, usa as fontes padrão do módulo
            self.font_regular = "helv"   # Helvetica Regular
            self.font_bold = "helvB"     # Helvetica Bold
        
        self.ativos_filter = AtivosQuerysetMixin().ativos_filter
    
    def desenhar_cabecalho(self) -> int:
        # Passo 3: Definir um ponto de partida para inserir texto.
        # As coordenadas (x, y) começam no canto superior esquerdo. O eixo Y cresce para baixo.
        ponto = pymupdf.Point(*self.ponto_inicial)
        
        # Passo 4: Inserir texto na página (usa a fonte definida no __init__).
        self.page.insert_text(ponto, f"{self.nome} - {self.request.empresa.razao_social}", fontsize=self.font_sizes['title'], fontname=self.font_bold)
        
        # Movemos o ponto para baixo para a próxima linha de texto.
        ponto.y += 25
        self.page.insert_text(ponto, f"Mês de referência: {self.mes_referencia}", fontsize=self.font_sizes['small'], fontname=self.font_regular)

        ponto.y += 20
        self.page.insert_text(ponto, f"Emitido por: {self.emissor_nome}", fontsize=self.font_sizes['small'], fontname=self.font_regular)
        
        # Adiciona uma linha horizontal para separar o cabeçalho.
        ponto.y += 20
        self.page.draw_line(ponto, pymupdf.Point(ponto.x + 500, ponto.y))
        
        # Retorna a próxima posição Y disponível para continuar desenhando.
        return ponto.y + 35

    def desenhar_corpo(self, y_inicial: int) -> int:
        ponto = pymupdf.Point(50, y_inicial)

        if len(self.lista_execucao) > 0:
            for funcao in self.lista_execucao:
                ponto.y = funcao(ponto.y)

                # after section, add some spacing
                ponto.y += 10
                self.page.draw_line(ponto, pymupdf.Point(ponto.x + 500, ponto.y))

                # leave more padding for next section
                ponto.y += 25
        else:
            self.page.insert_text(
                ponto,
                "Corpo base. Adicione novas seções na lista de execução.",
                fontsize=self.font_sizes['title'],
                fontname=self.font_bold,
            )

        return ponto.y

    def coletar_dados(self):
        """
        Hook principal para coleta de dados a serem inseridos no PDF a ser gerado.
        Ao implementar, atribuir elementos à própria instância de relatório.
        """
        raise NotImplementedError("Subclasses devem implementar o método 'coletar_dados'.")

    def desenhar(self) -> bytes:
        """
        Orquestra principal para geração e impressão do PDF.
        """
        self.coletar_dados()

        y_pos = self.desenhar_cabecalho()
        self.desenhar_corpo(y_pos)
    
    def gerar_pdf(self) -> bytes:
        """
        Entrega o documento em bytes para download.
        """
        self.desenhar()
        return self.doc.tobytes()


#* Especializados

class RelatorioAtividadeMensal(BaseRelatorio):
    """
    Gera um relatório de atividade mensal simples.

    Este relatório mostra um resumo do faturamento e do número de atendimentos
    para um determinado mês.
    """
    def __init__(self, request, ano, mes):
        super().__init__(request, ano, mes)
        self.nome = "Relatório de Atividade Mensal"
        self.lista_execucao = [
            self.desenhar_relatorio_agendamentos,
            self.desenhar_relatorio_trabalhadores
        ]

    def coletar_dados(self):
        """Busca e calcula os dados necessários no banco de dados."""
        #* Agendamentos
        base_agendamentos_mes = Agendamento.objects.filter(
            self.ativos_filter,
            empresa=self.request.empresa,
            data_agendado__date__gte=self.data_inicio,
            data_agendado__date__lte=self.data_fim
        )

        agendamentos_finalizados = base_agendamentos_mes.filter(status=AGENDAMENTO_STATUS_FINALIZADO)
        agendamentos_cancelados = base_agendamentos_mes.filter(status=AGENDAMENTO_STATUS_CANCELADO)

        self.faturamento_total_mes = agendamentos_finalizados.aggregate(total=Sum('servico__preco'))['total'] or 0.0
        self.total_agendamentos_finalizados = agendamentos_finalizados.count()
        self.faturamento_total_cancelado = agendamentos_cancelados.aggregate(total=Sum('servico__preco'))['total'] or 0.0
        self.total_agendamentos_cancelados = agendamentos_cancelados.count()


        #* Trabalhadores
        base_trabalhadores_atividade = (
            Trabalhador.objects.filter(
                self.ativos_filter,
                empresa=self.request.empresa,
                agendamentos__ativo=True,
                agendamentos__data_agendado__date__gte=self.data_inicio,
                agendamentos__data_agendado__date__lte=self.data_fim
            ).annotate(
                total_finalizados=Count(
                    "agendamentos", 
                    filter=(
                        Q(
                            agendamentos__status=AGENDAMENTO_STATUS_FINALIZADO, 
                            agendamentos__ativo=True
                        )
                    )
                ),
                total_cancelados=Count(
                    "agendamentos", 
                    filter=(
                        Q(
                            agendamentos__status=AGENDAMENTO_STATUS_CANCELADO, 
                            agendamentos__ativo=True
                        )
                    )
                ),
                valor_arrecadado_total=Sum(
                    "agendamentos__servico__preco",
                    filter=(
                        Q(
                            agendamentos__status=AGENDAMENTO_STATUS_FINALIZADO, 
                            agendamentos__ativo=True
                        )
                    )
                )
            )
        )

        self.trabalhadores_mais_agendamentos_finalizados = (
            base_trabalhadores_atividade
            .values("id", "nome")
            .order_by('-total_finalizados')[:3]
        )
        self.trabalhadores_mais_agendamentos_total = (
            base_trabalhadores_atividade
            .values("id", "nome")
            .order_by('-total_cancelados')[:3]
        )
        self.trabalhadores_maior_faturamento_total = (
            base_trabalhadores_atividade
            .values("id", "nome")
            .order_by('-valor_arrecadado_total')[:3]
        )


    def desenhar_relatorio_agendamentos(self, y_inicial: int) -> int:
        #Agendamentos
        ponto = pymupdf.Point(50, y_inicial)
        self.page.insert_text(ponto, "Resumo do Mês", fontsize=self.font_sizes['title'], fontname=self.font_bold)

        ponto.x += 20
        
        ponto.y += 25
        self.page.insert_text(ponto, f"Faturamento Total: {ConversionHelper.formatar_moeda(self.faturamento_total_mes)}", fontsize=self.font_sizes['sub-title'], fontname=self.font_bold)
        ponto.y += 17
        self.page.insert_text(ponto, f"Total de Atendimentos Realizados/Finalizados: {self.total_agendamentos_finalizados}", fontsize=self.font_sizes['small'], fontname=self.font_regular)

        ponto.y += 25
        self.page.insert_text(ponto, f"Faturamento Total Perdido: {ConversionHelper.formatar_moeda(self.faturamento_total_cancelado)}", fontsize=self.font_sizes['sub-title'], fontname=self.font_bold)
        ponto.y += 17
        self.page.insert_text(ponto, f"Total de Atendimentos Cancelados: {self.total_agendamentos_cancelados}", fontsize=self.font_sizes['small'], fontname=self.font_regular)

        return ponto.y


    def desenhar_relatorio_trabalhadores(self, y_inicial: int) -> int:
        ponto = pymupdf.Point(50, y_inicial)
        self.page.insert_text(ponto, "Resumo de funcionários", fontsize=self.font_sizes['title'], fontname=self.font_bold)

        ponto.x += 20

        ponto.y += 30
        i: int = 0
        self.page.insert_text(ponto, f"Top 3 funcionários com mais atendimentos finalizados", fontsize=self.font_sizes['sub-title'], fontname=self.font_bold)
        for item in self.trabalhadores_mais_agendamentos_finalizados:
            i += 1
            ponto.y += 20
            ponto_indentado = pymupdf.Point(ponto.x + 20, ponto.y)
            self.page.insert_text(ponto_indentado, f"{i}. {item.get('nome', '')}: {item.get('total_finalizados')} atendimentos finalizados.", fontsize=self.font_sizes['small'], fontname=self.font_regular)

        ponto.y += 30
        i: int = 0
        self.page.insert_text(ponto, f"Top 3 funcionários com mais atendimentos cancelados", fontsize=self.font_sizes['sub-title'], fontname=self.font_bold)
        for item in self.trabalhadores_mais_agendamentos_total:
            i += 1
            ponto.y += 20
            ponto_indentado = pymupdf.Point(ponto.x + 20, ponto.y)
            self.page.insert_text(ponto_indentado, f"{i}. {item.get('nome', '')}: {item.get('total_cancelados')} atendimentos cancelados.", fontsize=self.font_sizes['small'], fontname=self.font_regular)

        ponto.y += 30
        i: int = 0
        self.page.insert_text(ponto, f"Top 3 funcionários que geraram maior faturamento", fontsize=self.font_sizes['sub-title'], fontname=self.font_bold)
        for item in self.trabalhadores_maior_faturamento_total:
            i += 1
            ponto.y += 20
            ponto_indentado = pymupdf.Point(ponto.x + 20, ponto.y)
            self.page.insert_text(ponto_indentado, f"{i}. {item.get('nome', '')}: {ConversionHelper.formatar_moeda(item.get('valor_arrecadado_total'))} total.", fontsize=self.font_sizes['small'], fontname=self.font_regular)

        return ponto.y

class RelatorioClientesMensal(BaseRelatorio):
    def __init__(self, request, ano, mes):
        super().__init__(request, ano, mes)
        self.nome = "Relatório de Clientes Mensal"
        self.lista_execucao = [
            self.desenhar_relatorio_clientes_atuais,
            self.desenhar_relatorio_clientes_recorrentes,
            self.desenhar_relatorio_clientes_inativos
        ]

    def coletar_dados(self):
        #* Clientes Atuais
        base_clientes = Cliente.objects.filter(self.ativos_filter, empresa=self.request.empresa)

        self.total_clientes_novos = base_clientes.filter(
            data_criado__gte=self.data_inicio,
            data_criado__lte=self.data_fim
        ).count()

        base_clientes_atividade = (
            base_clientes.filter(
                agendamentos__ativo=True,
                agendamentos__data_agendado__gte=self.data_inicio,
                agendamentos__data_agendado__lte=self.data_fim
            )
            .values("id", "nome")
            .annotate(
                total_marcados=Count("agendamentos"),
                total_finalizados=Count(
                    "agendamentos", 
                    filter=(
                        Q(
                            agendamentos__status=AGENDAMENTO_STATUS_FINALIZADO, 
                            agendamentos__ativo=True
                        )
                    )
                ),
                total_cancelados=Count(
                    "agendamentos", 
                    filter=(
                        Q(
                            agendamentos__status=AGENDAMENTO_STATUS_CANCELADO, 
                            agendamentos__ativo=True
                        )
                    )
                ),
            )
        )

        #quais clientes com mais atendimentos marcados
        self.clientes_mais_agendamentos_marcados = (
            base_clientes_atividade
            .order_by('-total_marcados')[:3]
        )
        #quais clientes com mais atendimentos finalizados
        self.clientes_mais_agendamentos_finalizados = (
            base_clientes_atividade
            .order_by('-total_finalizados')[:3]
        )
        #quais clientes com mais atendimentos cancelados
        self.clientes_mais_agendamentos_cancelados = (
            base_clientes_atividade
            .order_by('-total_cancelados')[:3]
        )

        #Cliente que gerou maior faturamento
        self.cliente_maior_faturamento_total = (
            base_clientes
            .annotate(faturamento_total=Sum("agendamentos__servico__preco"))
            .order_by("-faturamento_total")
            .first()
        )
        if self.cliente_maior_faturamento_total and self.cliente_maior_faturamento_total.faturamento_total <= 0:
            self.cliente_maior_faturamento_total = None

        #* Clientes recorrentes
        base_agendamentos_clientes_mes = base_clientes.filter(
            agendamentos__ativo=True,
            agendamentos__data_agendado__gte=self.data_inicio,
            agendamentos__data_agendado__lte=self.data_fim,
        )
        self.total_clientes_unicos = base_agendamentos_clientes_mes.distinct().count()

        self.clientes_recorrentes = (
            base_agendamentos_clientes_mes
            .values("id", "nome", "telefone")
            .annotate(
                total_agendamentos=Count("agendamentos", 
                    filter=(
                        Q(agendamentos__status__in=[
                            AGENDAMENTO_STATUS_PENDENTE,
                            AGENDAMENTO_STATUS_EXECUTANDO, 
                            AGENDAMENTO_STATUS_FINALIZADO
                        ], agendamentos__ativo=True)
                    )
                )
            ).filter(total_agendamentos__gt=1)
            .order_by('-total_agendamentos')
        )

        # nn%
        try:
            calculo_recorrencia = (self.clientes_recorrentes.count() / self.total_clientes_unicos) * 100
        except ZeroDivisionError:
            calculo_recorrencia = 0
        self.porcentagem_recorrencia = f"{calculo_recorrencia:.2f}%"

        self.top_clientes_recorrentes = (
            self.clientes_recorrentes.order_by('-total_agendamentos')[:3]
        )

        self.top_clientes_antigos_recorrentes = (
            base_clientes.filter(
                agendamentos__ativo=True,
                data_criado__lt=self.data_inicio,
                agendamentos__data_agendado__gte=(self.data_inicio - timedelta(days=30 * 6)), # Últimos 6 meses
                agendamentos__data_agendado__lte=self.data_fim # Até o final do mês atual
            ).annotate(
                total_agendamentos=Count("agendamentos", 
                    filter=(
                        Q(agendamentos__status__in=[
                            AGENDAMENTO_STATUS_PENDENTE,
                            AGENDAMENTO_STATUS_EXECUTANDO, 
                            AGENDAMENTO_STATUS_FINALIZADO
                        ], agendamentos__ativo=True)
                    )
                )
            ).filter(total_agendamentos__gt=1) # Clientes com mais de 1 agendamento no período
            .order_by('-total_agendamentos')
        )[:3]

        
        #* Clientes inativos
        # Clientes que não tiveram agendamentos nos últimos 3 meses
        clientes_inativos = (
            base_clientes
            .annotate(
                total_agendamentos_periodo=Count(
                    "agendamentos",
                    filter=Q(
                        agendamentos__ativo=True,
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
                    filter=(
                        Q(agendamentos__status__in=[
                            AGENDAMENTO_STATUS_PENDENTE,
                            AGENDAMENTO_STATUS_EXECUTANDO, 
                            AGENDAMENTO_STATUS_FINALIZADO
                        ], agendamentos__ativo=True)
                    )
                )
            ).filter(
                total_agendamentos_geral__gt=1
            ).order_by("-data_criado")
        )[:3]


    def desenhar_relatorio_clientes_atuais(self, y_inicial: int) -> int:
        ponto = pymupdf.Point(50, y_inicial)
        self.page.insert_text(ponto, "Resumo de Clientes Atuais", fontsize=self.font_sizes['title'], fontname=self.font_bold)

        ponto.y += 25
        self.page.insert_text(ponto, "Total de Clientes Novos:", fontsize=self.font_sizes['sub-title'], fontname=self.font_regular)
        # Ajuste de posicionamento para o valor do total de clientes novos
        self.page.insert_text(pymupdf.Point(ponto.x + 136, ponto.y), str(self.total_clientes_novos), fontsize=self.font_sizes['sub-title'], fontname=self.font_bold)

        ponto.x += 20

        ponto.y += 26
        i: int = 0
        self.page.insert_text(ponto, f"Top 3 clientes com mais agendamentos marcados", fontsize=self.font_sizes['sub-title'], fontname=self.font_bold)
        for item in self.clientes_mais_agendamentos_marcados:
            i += 1
            ponto.y += 20
            ponto_indentado = pymupdf.Point(ponto.x + 17, ponto.y)
            self.page.insert_text(ponto_indentado, f"{i}. {item.get('nome', '')}: {item.get('total_marcados')} agendamentos.", fontsize=self.font_sizes['small'], fontname=self.font_regular)

        ponto.y += 20
        i: int = 0
        self.page.insert_text(ponto, f"Top 3 clientes com mais agendamentos finalizados", fontsize=self.font_sizes['sub-title'], fontname=self.font_bold)
        for item in self.clientes_mais_agendamentos_finalizados:
            i += 1
            ponto.y += 20
            ponto_indentado = pymupdf.Point(ponto.x + 17, ponto.y)
            self.page.insert_text(ponto_indentado, f"{i}. {item.get('nome', '')}: {item.get('total_finalizados')} agendamentos.", fontsize=self.font_sizes['small'], fontname=self.font_regular)

        ponto.y += 20
        i: int = 0
        self.page.insert_text(ponto, f"Top 3 clientes com mais agendamentos cancelados", fontsize=self.font_sizes['sub-title'], fontname=self.font_bold)
        for item in self.clientes_mais_agendamentos_cancelados:
            i += 1
            ponto.y += 20
            ponto_indentado = pymupdf.Point(ponto.x + 17, ponto.y)
            self.page.insert_text(ponto_indentado, f"{i}. {item.get('nome', '')}: {item.get('total_cancelados')} agendamentos.", fontsize=self.font_sizes['small'], fontname=self.font_regular)

        ponto.y += 30
        self.page.insert_text(ponto, f"Cliente que gerou maior faturamento total no mês", fontsize=self.font_sizes['sub-title'], fontname=self.font_bold)
        ponto.y += 20
        ponto_indentado = pymupdf.Point(ponto.x + 17, ponto.y)
        if not self.cliente_maior_faturamento_total:
            self.page.insert_text(ponto_indentado, "Nenhum cliente com faturamento encontrado.", fontsize=self.font_sizes['small'], fontname=self.font_regular)
            return ponto.y
        else: 
            self.page.insert_text(ponto_indentado, f"{self.cliente_maior_faturamento_total.nome}: {ConversionHelper.formatar_moeda(self.cliente_maior_faturamento_total.faturamento_total)} agendamentos.", fontsize=self.font_sizes['small'], fontname=self.font_regular)
        ponto.y += 15
        ponto_indentado = pymupdf.Point(ponto.x + 17, ponto.y)
        self.page.insert_text(ponto_indentado, f"(telefone: {self.cliente_maior_faturamento_total.telefone})", fontsize=self.font_sizes['small'], fontname=self.font_regular)

        return ponto.y
    
    def desenhar_relatorio_clientes_recorrentes(self, y_inicial: int) -> int:
        ponto = pymupdf.Point(50, y_inicial)
        self.page.insert_text(ponto, "Resumo de Clientes Recorrentes", fontsize=self.font_sizes['title'], fontname=self.font_bold)

        ponto.y += 25
        self.page.insert_text(ponto, "Total de Clientes Únicos:", fontsize=self.font_sizes['small'], fontname=self.font_regular)
        # Ajuste de posicionamento para o valor do total de clientes únicos
        self.page.insert_text(pymupdf.Point(ponto.x + 114, ponto.y), str(self.total_clientes_unicos), fontsize=self.font_sizes['small'], fontname=self.font_bold)
        
        ponto.y += 15
        self.page.insert_text(ponto, "Total de Clientes Recorrentes:", fontsize=self.font_sizes['small'], fontname=self.font_regular)
        # Ajuste de posicionamento para o valor do total de clientes recorrentes
        self.page.insert_text(pymupdf.Point(ponto.x + 139, ponto.y), str(self.clientes_recorrentes.count()), fontsize=self.font_sizes['small'], fontname=self.font_bold)
        
        ponto.y += 15
        self.page.insert_text(ponto, f"Porcentagem de recorrência do mês: {self.porcentagem_recorrencia} dos clientes.", fontsize=self.font_sizes['sub-title'], fontname=self.font_bold)

        ponto.y += 30
        i: int = 0
        self.page.insert_text(ponto, f"Top 3 clientes mais recorrentes", fontsize=self.font_sizes['sub-title'], fontname=self.font_bold)
        for item in self.top_clientes_recorrentes:
            i += 1
            ponto.y += 20
            ponto_indentado = pymupdf.Point(ponto.x + 17, ponto.y)
            self.page.insert_text(ponto_indentado, f"{i}. {item.get('nome', '')}: {item.get('total_agendamentos')} agendamentos.", fontsize=self.font_sizes['small'], fontname=self.font_regular)

        ponto.y += 20
        i: int = 0
        self.page.insert_text(ponto, f"Top 3 clientes recorrentes antigos (nos últimos 6 meses)", fontsize=self.font_sizes['sub-title'], fontname=self.font_bold)

        if len(self.top_clientes_antigos_recorrentes) == 0:
            ponto.y += 20
            self.page.insert_text(pymupdf.Point(ponto.x + 15, ponto.y), "Nenhum recorrente antigo encontrado.", fontsize=self.font_sizes['small'])
        else:
            for item in self.top_clientes_antigos_recorrentes:
                i += 1
                ponto.y += 20
                ponto_indentado = pymupdf.Point(ponto.x + 17, ponto.y)
                self.page.insert_text(ponto_indentado, f"{i}. {item.nome}: {item.total_agendamentos} agendamentos.", fontsize=self.font_sizes['small'], fontname=self.font_regular)

        return ponto.y
    
    def desenhar_relatorio_clientes_inativos(self, y_inicial: int) -> int:
        ponto = pymupdf.Point(50, y_inicial)
        self.page.insert_text(ponto, "Resumo de Clientes Inativos", fontsize=self.font_sizes['title'], fontname=self.font_bold)

        ponto.y += 25
        self.page.insert_text(ponto, f"Total de Clientes Inativos (nos últimos 6 meses): {self.total_clientes_inativos}", fontsize=self.font_sizes['small'], fontname=self.font_regular)

        ponto.y += 20
        i: int = 0
        self.page.insert_text(ponto, f"Top 3 recorrentes atualmente inativos (nos últimos 6 meses)", fontsize=self.font_sizes['sub-title'], fontname=self.font_bold)
        
        if len(self.clientes_inativos_antigos_recorrentes) == 0: # Alterado para a lista correta de inativos recorrentes
            ponto.y += 20
            self.page.insert_text(pymupdf.Point(ponto.x + 15, ponto.y), "Nenhum recorrente inativo encontrado.", fontsize=self.font_sizes['small'])
        else:
            for item in self.clientes_inativos_antigos_recorrentes: # Limitar aos top 3
                i += 1
                ponto.y += 20
                ponto_indentado = pymupdf.Point(ponto.x + 17, ponto.y)
                self.page.insert_text(ponto_indentado, f"{i}. {item.nome}: {item.total_agendamentos_geral} agendamentos.", fontsize=self.font_sizes['small'], fontname=self.font_regular)

        return ponto.y
