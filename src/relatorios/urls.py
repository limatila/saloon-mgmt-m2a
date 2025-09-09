from django.urls import path
from .views import RelatorioAtividadeMensalView

app_name = 'relatorios'

urlpatterns = [
    path('', RelatorioAtividadeMensalView.as_view(), name='list'),
    path('atividade-mensal/', RelatorioAtividadeMensalView.as_view(), name='mensal') # Exemplo de URL: /relatorios/atividade-mensal/?ano=2023&mes=10
]