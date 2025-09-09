from datetime import datetime

from django.http import HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from cadastros.empresas.mixins import EscopoEmpresaQuerysetMixin
from relatorios.reports import gerar_relatorio_atividade_mensal


class BaseReportView(LoginRequiredMixin, EscopoEmpresaQuerysetMixin, View):
    """
    View base para gerar e retornar um relatório em PDF.
    Subclasses devem implementar o método `generate_pdf`.
    """
    filename_prefix = 'relatorio'

    def get_file_report_name(self) -> str:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
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

class RelatorioAtividadeMensalView(BaseReportView):
    filename_prefix = 'relatorio_mensal'

    def generate_pdf(self, *args, **kwargs) -> bytes:
        ano = datetime.now().year
        mes = datetime.now().month
        return gerar_relatorio_atividade_mensal(empresa=self.request.empresa, ano=ano, mes=mes)
