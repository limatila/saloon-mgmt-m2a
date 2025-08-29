from django.urls import path, include

from cadastros.empresas.views import EmpresaListView


app_name = "empresas"

urlpatterns = [
    path('', EmpresaListView.as_view(), name="list")
]
