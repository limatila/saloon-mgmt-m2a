import calendar
from datetime import datetime

from django.db.models import Q, Count, Sum
from django.contrib.staticfiles import finders
import pymupdf

from cadastros.clientes.models import Cliente
from cadastros.trabalhadores.models import Trabalhador
from servicos.agendamentos.models import Agendamento
from servicos.agendamentos.choices import (
    AGENDAMENTO_STATUS_FINALIZADO,
    AGENDAMENTO_STATUS_CANCELADO
)


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
        self.mes_referencia = f"{self.mes} / {self.ano}"
        self.emissor_nome = (
            self.request.user.get_full_name()
            or self.request.user.username
            or getattr(self.request, 'empresa', None) and self.request.empresa.nome_fantasia
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

    #TODO refatorar para um helper core
    def formatar_moeda(self, valor: float) -> str:
        """Helper para formatar um valor numérico para a moeda brasileira (BRL)."""
        if valor is None:
            valor = 0.0
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    def desenhar_cabecalho(self) -> int:
        # Passo 3: Definir um ponto de partida para inserir texto.
        # As coordenadas (x, y) começam no canto superior esquerdo. O eixo Y cresce para baixo.
        ponto = pymupdf.Point(*self.ponto_inicial)
        
        # Passo 4: Inserir texto na página (usa a fonte definida no __init__).
        self.page.insert_text(ponto, f"Relatório de Atividade Mensal - {self.request.empresa.razao_social}", fontsize=self.font_sizes['title'], fontname=self.font_bold)
        
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
                self.page.draw_line(ponto, pymupdf.Point(ponto.x + 500, ponto.y))
                #separação de seções
        else:
            self.page.insert_text(ponto, f"Corpo base. Adicione novas seções na lista de execução.", fontsize=self.font_sizes['title'], fontname=self.font_bold)

        return ponto.y + 20

    def coletar_dados(self) -> bytes:
        """
        Hook principal para coleta de dados a serem inseridos no PDF a ser gerado.
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

class RelatorioAgendamentosMensal(BaseRelatorio):
    """
    Gera um relatório de atividade mensal simples.

    Este relatório mostra um resumo do faturamento e do número de atendimentos
    para um determinado mês.
    """
    def __init__(self, request, ano, mes):
        super().__init__(request, ano, mes)
        self.lista_execucao = [
            self.desenhar_relatorio_agendamentos,
            self.desenhar_relatorio_trabalhadores
        ]

    def coletar_dados(self):
        """Busca e calcula os dados necessários no banco de dados."""
        _, ultimo_dia = calendar.monthrange(self.ano, self.mes)
        data_inicio = datetime(self.ano, self.mes, 1)
        data_fim = datetime(self.ano, self.mes, ultimo_dia).replace(hour=23, minute=59, second=59)

        #Agendamentos
        agendamentos_finalizados = Agendamento.objects.filter(
            empresa=self.request.empresa,
            status=AGENDAMENTO_STATUS_FINALIZADO,
            data_agendado__date__gte=data_inicio,
            data_agendado__date__lte=data_fim
        )
        agendamentos_cancelados = Agendamento.objects.filter(
            empresa=self.request.empresa,
            status=AGENDAMENTO_STATUS_CANCELADO,
            data_agendado__date__gte=data_inicio,
            data_agendado__date__lte=data_fim
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
                agendamentos__data_agendado__date__gte=data_inicio,
                agendamentos__data_agendado__date__lte=data_fim
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

    def desenhar_relatorio_agendamentos(self, y_inicial: int):
        #Agendamentos
        ponto = pymupdf.Point(50, y_inicial)
        self.page.insert_text(ponto, "Resumo do Mês", fontsize=self.font_sizes['title'], fontname=self.font_bold)

        ponto.y += 25
        self.page.insert_text(ponto, f"Faturamento Total: {self.formatar_moeda(self.faturamento_total_mes)}", fontsize=self.font_sizes['sub-title'], fontname=self.font_bold)
        ponto.y += 17
        self.page.insert_text(ponto, f"Total de Atendimentos Realizados/Finalizados: {self.total_agendamentos_finalizados}", fontsize=self.font_sizes['small'], fontname=self.font_regular)

        ponto.y += 25
        self.page.insert_text(ponto, f"Faturamento Total Perdido: {self.formatar_moeda(self.faturamento_total_cancelado)}", fontsize=self.font_sizes['sub-title'], fontname=self.font_bold)
        ponto.y += 17
        self.page.insert_text(ponto, f"Total de Atendimentos Cancelados: {self.total_agendamentos_cancelados}", fontsize=self.font_sizes['small'], fontname=self.font_regular)

        return ponto.y + 20


    def desenhar_relatorio_trabalhadores(self, y_inicial: int):
        ponto = pymupdf.Point(50, y_inicial)

        #Trabalhadores
        ponto.y += 35
        self.page.insert_text(ponto, "Overview de funcionários", fontsize=self.font_sizes['title'], fontname=self.font_bold)

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
        for item in self.trabalhadores_mais_agendamentos_cancelados:
            i += 1
            ponto.y += 20
            ponto_indentado = pymupdf.Point(ponto.x + 20, ponto.y)
            self.page.insert_text(ponto_indentado, f"{i}. {item.get('nome', '')}: {item.get('total_cancelados')} atendimentos cancelados.", fontsize=self.font_sizes['small'], fontname=self.font_regular)

        ponto.y += 30
        i: int = 0
        self.page.insert_text(ponto, f"Top 3 funcionários com maior faturamento", fontsize=self.font_sizes['sub-title'], fontname=self.font_bold)
        for item in self.trabalhadores_maior_faturamento_total:
            i += 1
            ponto.y += 20
            ponto_indentado = pymupdf.Point(ponto.x + 20, ponto.y)
            self.page.insert_text(ponto_indentado, f"{i}. {item.get('nome', '')}: {self.formatar_moeda(item.get('valor_arrecadado_total'))}.", fontsize=self.font_sizes['small'], fontname=self.font_regular)

        return ponto.y + 20

class RelatorioClientesMensal(BaseRelatorio):
    def coletar_dados(self):
        self.span = 'span'