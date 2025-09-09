from datetime import datetime

from django.http import HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from cadastros.empresas.mixins import EscopoEmpresaQuerysetMixin

from relatorios.relatorios import RelatorioAgendamentoMensal


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


#* Especializados: page, relatórios

class RelatorioAgendamentosMensalView(BaseReportView):
    """
    Cria um PDF de atividade mensal, consolidando dados de agendamentos,
    faturamentos, e trabalhadores notaveis.
    """
    filename_prefix = 'relatorio_agendamentos_mensal'

    def generate_pdf(self, *args, **kwargs) -> bytes:        
        # Get year and month from GET parameters, defaulting to current year/month
        try:
            ano = int(self.request.GET.get('ano', datetime.now().year))
            mes = int(self.request.GET.get('mes', datetime.now().month))
        except ValueError:
            raise Exception("Valores de ano e mês inseridos na geração de PDF não são válidos.")

        relatorio = RelatorioAgendamentoMensal(self.request, ano, mes)
        return relatorio.gerar()
