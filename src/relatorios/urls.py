from django.urls import path
from .views import RelatorioAgendamentosMensalView

app_name = 'relatorios'

urlpatterns = [
    path('', RelatorioAgendamentosMensalView.as_view(), name='list'),
    path('atividade-mensal/', RelatorioAgendamentosMensalView.as_view(), name='mensal') # Exemplo de URL: /relatorios/atividade-mensal/?ano=2023&mes=10
]