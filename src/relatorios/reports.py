import pymupdf
import calendar
from datetime import date
from django.db.models import Sum

from servicos.agendamentos.models import Agendamento
from servicos.agendamentos.choices import AGENDAMENTO_STATUS_FINALIZADO
from cadastros.empresas.models import Empresa

class BaseReport:
    """
    Classe base para a criação de relatórios em PDF (PyMuPDF).
    
    Esta classe lida com a inicialização do documento PDF e fornece
    métodos auxiliares que podem ser usados por qualquer relatório.
    """
    def __init__(self):        
        # Passo 1: Criar um documento PDF em branco na memória.
        # O 'pymupdf.open()' sem argumentos cria um novo documento.
        self.doc = pymupdf.open()
        
        # Passo 2: Adicionar uma página em branco ao documento.
        # As páginas são adicionadas e podem ser acessadas pelo índice, como doc[0].
        self.page = self.doc.new_page()

    def formatar_moeda(self, valor: float) -> str:
        """Helper para formatar um valor numérico para a moeda brasileira (BRL)."""
        if valor is None:
            valor = 0.0
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    def generate(self) -> bytes:
        """
        Método principal que orquestra a criação do PDF.
        As subclasses devem sobrescrever este método para adicionar o conteúdo.
        """
        raise NotImplementedError("Subclasses devem implementar o método 'generate'.")


class RelatorioAtividadeMensal(BaseReport):
    """
    Gera um relatório de atividade mensal simples.
    
    Este relatório mostra um resumo do faturamento e do número de atendimentos
    para um determinado mês.
    """
    def __init__(self, empresa, ano, mes):
        super().__init__()
        self.empresa = empresa
        self.ano = ano
        self.mes = mes

    def coletar_dados(self):
        """Busca e calcula os dados necessários no banco de dados."""
        _, ultimo_dia = calendar.monthrange(self.ano, self.mes)
        data_inicio = date(self.ano, self.mes, 1)
        data_fim = date(self.ano, self.mes, ultimo_dia)

        agendamentos_finalizados = Agendamento.objects.filter(
            empresa=self.empresa,
            status=AGENDAMENTO_STATUS_FINALIZADO,
            data_agendado__date__gte=data_inicio,
            data_agendado__date__lte=data_fim
        )

        # Usamos 'aggregate' para calcular a soma e 'count' para a contagem.
        self.faturamento_total = agendamentos_finalizados.aggregate(total=Sum('servico__preco'))['total'] or 0.0
        self.total_atendimentos = agendamentos_finalizados.count()

    def desenhar_cabecalho(self):
        """Desenha o título e o período do relatório no topo da página."""
        # Passo 3: Definir um ponto de partida para inserir texto.
        # As coordenadas (x, y) começam no canto superior esquerdo. O eixo Y cresce para baixo.
        ponto = pymupdf.Point(50, 72)
        
        nome_mes = calendar.month_name[self.mes].title()
        
        # Passo 4: Inserir texto na página.
        # Usamos 'page.insert_text()' para adicionar texto em uma coordenada específica.
        self.page.insert_text(ponto, f"Relatório de Atividade Mensal - {self.empresa.nome_fantasia}", fontsize=16, fontname="helv-bold")
        
        # Movemos o ponto para baixo para a próxima linha de texto.
        ponto.y += 20
        self.page.insert_text(ponto, f"Período: {nome_mes} de {self.ano}", fontsize=11)
        
        # Adiciona uma linha horizontal para separar o cabeçalho.
        ponto.y += 15
        self.page.draw_line(pymupdf.Point(50, ponto.y), pymupdf.Point(550, ponto.y))
        
        # Retorna a próxima posição Y disponível para continuar desenhando.
        return ponto.y + 20

    def desenhar_corpo(self, y_inicial: int):
        """Desenha o conteúdo principal do relatório."""
        ponto = pymupdf.Point(50, y_inicial)
        self.page.insert_text(ponto, "Resumo do Mês", fontsize=14, fontname="helv-bold")
        
        ponto.y += 25
        self.page.insert_text(ponto, f"Faturamento Total: {self.formatar_moeda(self.faturamento_total)}", fontsize=11)
        
        ponto.y += 20
        self.page.insert_text(ponto, f"Total de Atendimentos Realizados: {self.total_atendimentos}", fontsize=11)

    def generate(self) -> bytes:
        """Orquestra a criação do relatório mensal."""
        self.coletar_dados()
        y_pos = self.desenhar_cabecalho()
        self.desenhar_corpo(y_pos)
        
        # Passo 5: Finalizar o documento e obter seus bytes para a resposta HTTP.
        return self.doc.tobytes()


# --- Função de Interface Pública ---

def gerar_relatorio_atividade_mensal(empresa: Empresa, ano: int, mes: int) -> bytes:
    """
    Cria um PDF de atividade mensal, consolidando dados de agendamentos,
    clientes e faturamento.
    
    Esta função serve como uma interface simples, delegando a lógica de
    criação para a classe RelatorioAtividadeMensal.
    """
    relatorio = RelatorioAtividadeMensal(empresa, ano, mes)
    return relatorio.generate()
