from datetime import datetime
from urllib.parse import urlencode

from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy

from core.bases.views import BasePageView
from cadastros.empresas.mixins import ContextoEmpresaMixin
from .relatorios import RelatorioAtividadeMensal, RelatorioClientesMensal
from relatorios.types import RelatorioAcesso, RelatorioGrupo


class BaseReportView(LoginRequiredMixin, ContextoEmpresaMixin, View):
    """
    View base para gerar e retornar um relatório em PDF.
    Subclasses devem implementar o método `generate_pdf`.
    """
    filename_prefix = 'relatorio'

    def get_file_report_name(self) -> str:
        timestamp = datetime.now().strftime('%Y-%m-%d_%Hh%Mm%Ss')
        return f'{self.filename_prefix} ({timestamp}).pdf'

    def generate_pdf(self, *args, **kwargs) -> bytes:
        """
        Hook para implementação de geração do PDF.
        
        - Returns:
            Este método precisa retornar os bytes do arquivo PDF.
        """
        raise NotImplementedError(
            "Subclasses de BaseReportView devem implementar o método \'generate_pdf\'."
        )

    def get(self, request, *args, **kwargs):
        pdf_bytes = self.generate_pdf(request)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{self.get_file_report_name()}"'
        return response


class BaseReportMensalView(BaseReportView):
    def get_params_from_request(self):
        # Get year and month from GET parameters, defaulting to current year/month
        try:
            return {
                'ano': int(self.request.GET.get('ano', datetime.now().year)),
                'mes': int(self.request.GET.get('mes', datetime.now().month))
            }
        except ValueError:
            raise Exception("Valores de ano e mês inseridos na geração de PDF não são válidos.")


#* Especializados: page, relatórios

class SelecaoRelatoriosView(LoginRequiredMixin, ContextoEmpresaMixin, BasePageView):
    template_name = 'relatorios/selecao-relatorios.html'

    def get_ano_mes(self) -> tuple[int, int]:
        """Retorna ano e mês da query params, ou defaults atuais."""
        agora = datetime.now()

        try:
            ano = int(self.request.GET.get("ano", agora.year))
        except ValueError:
            ano = agora.year

        try:
            mes = int(self.request.GET.get("mes", agora.month))
        except ValueError:
            mes = agora.month

        return (mes, ano)

    def get_relatorios_list(self) -> list[RelatorioAcesso]:
        """Retorna a lista de relatórios como RelatorioAcesso."""
        from relatorios.urls import urlpatterns, display_nomes

        mes, ano = self.get_ano_mes()
        relatorios: list[RelatorioAcesso] = []

        query_string = urlencode({"ano": ano, "mes": mes})  # adiciona ano/mes na URL

        for url in urlpatterns:
            nome_mostrado = display_nomes.get(url.name)
            if nome_mostrado:
                url_completo = f"{reverse_lazy(f'relatorios:{url.name}')}?{query_string}"
                relatorios.append(RelatorioAcesso(
                    nome=(nome_mostrado or url.name).replace("_", " ").title(),
                    url=url_completo
                ))
        return relatorios

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        mes, ano = self.get_ano_mes()
        contexto["title"] = "Lista de relatórios"
        contexto["description"] = "Selecione um relatório para exibição em PDF."
        contexto["ano"] = ano
        contexto["mes"] = mes

        # Agrupamento de exemplo: aqui você pode criar lógicas para múltiplos grupos
        relatorios = self.get_relatorios_list()
        contexto["relatorios_grupos"] = [
            RelatorioGrupo(nome="Relatórios Mensais", relatorios=relatorios)
        ]
        return contexto


class RelatorioAtividadeMensalView(BaseReportMensalView):
    """
    Cria um PDF de atividade mensal, consolidando dados de agendamentos,
    faturamentos, e trabalhadores notaveis.
    """
    filename_prefix = 'relatorio_agendamentos_mensal'

    def generate_pdf(self, *args, **kwargs) -> bytes:
        params: dict = self.get_params_from_request()
        relatorio = RelatorioAtividadeMensal(
            request=self.request,
            ano=params['ano'],
            mes=params['mes']
        )
        return relatorio.gerar_pdf()


class RelatorioClientesMensalView(BaseReportMensalView):
    """
    Cria um PDF de atividade mensal, consolidando dados de agendamentos,
    faturamentos, e trabalhadores notaveis.
    """
    filename_prefix = 'relatorio_clientes_mensal'

    def generate_pdf(self, *args, **kwargs) -> bytes:
        params: dict = self.get_params_from_request()
        relatorio = RelatorioClientesMensal(
            request=self.request,
            ano=params['ano'],
            mes=params['mes']
        )
        return relatorio.gerar_pdf()
