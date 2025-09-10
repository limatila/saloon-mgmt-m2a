from django.urls import path
from relatorios.views import SelecaoRelatoriosView, RelatorioAtividadeMensalView, RelatorioClientesMensalView

app_name = 'relatorios'

urlpatterns = [
    path('', SelecaoRelatoriosView.as_view(), name='list'),
    path('atividade-mensal/', RelatorioAtividadeMensalView.as_view(), name='atividade-mensal'), # Exemplo de URL: /relatorios/atividade-mensal/?ano=2023&mes=10
    path('clientes-mensal/', RelatorioClientesMensalView.as_view(), name='clientes-mensal')
]

#selecione urlpatterns que devem se motrados na listagem de relatórios
display_nomes: dict[str, str] = {
    #[urlpattern.name]: "nome para display"
    'atividade-mensal': "Relatório de Atividade Mensal",
    'clientes-mensal': "Relatório de Clientes Mensal"
}