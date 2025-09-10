from datetime import datetime

from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.urls import reverse_lazy

from core.bases.views import BasePageView
from cadastros.empresas.mixins import EscopoEmpresaQuerysetMixin

from .relatorios import RelatorioAgendamentosMensal, RelatorioClientesMensal


class BaseReportView(LoginRequiredMixin, EscopoEmpresaQuerysetMixin, View):
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
        pdf_bytes = self.generate_pdf(request, *args, **kwargs)
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

class SelecaoRelatoriosView(LoginRequiredMixin, EscopoEmpresaQuerysetMixin, BasePageView):
    template_name = 'relatorios/selecao-relatorios.html'

    def get_relatorios_list(self) -> list[dict[str, str]]:
        from relatorios.urls import urlpatterns, display_nomes

        relatorios = []
        for url in urlpatterns:
            nome_mostrado = display_nomes.get(url.name, None)
            if nome_mostrado:# só pega rotas nomeadas
                relatorios.append({
                    "nome": (nome_mostrado or url.name).replace("_", " ").title(),
                    "url": reverse_lazy(f"relatorios:{url.name}"),
                })
        return relatorios

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Lista de relatórios"
        contexto["description"] = "Selecione um relatório para exibição em PDF."
        contexto["relatorios_list"] = self.get_relatorios_list()
        return contexto


class RelatorioAgendamentosMensalView(BaseReportMensalView):
    """
    Cria um PDF de atividade mensal, consolidando dados de agendamentos,
    faturamentos, e trabalhadores notaveis.
    """
    filename_prefix = 'relatorio_agendamentos_mensal'

    def generate_pdf(self, *args, **kwargs) -> bytes:        
        params: dict = self.get_params_from_request()
        relatorio = RelatorioAgendamentosMensal(
            request=self.request,
            ano=params['ano'],
            mes=params['mes']
        )
        return relatorio.gerar()


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
        return relatorio.gerar()
