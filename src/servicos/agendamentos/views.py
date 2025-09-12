from django.views.generic import CreateView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404

from core.bases.views import BaseDynamicListView, BaseDynamicFormView, SelecaoDynamicListView
from cadastros.empresas.views import FieldsComEscopoEmpresaFormView
from cadastros.empresas.mixins import EscopoEmpresaQuerysetMixin
from servicos.agendamentos.models import Agendamento
from servicos.agendamentos.forms import AgendamentoForm
from servicos.agendamentos.mixins import AgendamentosSearchMixin
from servicos.agendamentos.choices import (
    AGENDAMENTO_STATUS_PENDENTE,
    AGENDAMENTO_STATUS_EXECUTANDO,
    AGENDAMENTO_STATUS_FINALIZADO 
)


#TODO verificar se está com LoginRequired -- bloqueante
class AgendamentoListView(AgendamentosSearchMixin, EscopoEmpresaQuerysetMixin, BaseDynamicListView):
    model = Agendamento

    def get_fields_display(self):
        return ['data_agendado', 'status', 'cliente', 'servico', 'trabalhador']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Lista de Agendamentos"
        return context


class AgendamentoCreateView(FieldsComEscopoEmpresaFormView, BaseDynamicFormView, CreateView):
    model = Agendamento
    form_class = AgendamentoForm
    success_url = reverse_lazy('servicos:agendamentos:list')

    def form_valid(self, form):
        return super().form_valid(form)


#* Funcionalidades
class FinalizarAgendamentoView(LoginRequiredMixin, AgendamentosSearchMixin, EscopoEmpresaQuerysetMixin, SelecaoDynamicListView):
    model = Agendamento
    condicao_agendamento_valido = (
        Q(status=AGENDAMENTO_STATUS_PENDENTE) | Q(status=AGENDAMENTO_STATUS_EXECUTANDO)
    )

    def get_fields_display(self):
        return ['data_agendado', 'status', 'cliente', 'servico', 'trabalhador']
    
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['title'] = "Finalize um agendamento"
        contexto['description'] = "Selecione o seu atendimento pendente / em execução."
        contexto['sidebar'] = True
        contexto['query'] = self.request.GET.get("query", "").strip()
        return contexto
    
    def post(self, request, *args, **kwargs):
        agendamento_id = self.get_selecao_or_redirect(request)

        if not agendamento_id:
            messages.warning(request, "⚠️ Você precisa selecionar um agendamento.")
            return redirect(request.path)  # back to the same page
        try:
            agendamento = get_object_or_404(
                Agendamento.objects.filter(self.condicao_agendamento_valido),
                id=agendamento_id
            )
            agendamento.status = AGENDAMENTO_STATUS_FINALIZADO
            agendamento.save()
            messages.success(request, "✅ Agendamento finalizado com sucesso!")
        except Agendamento.DoesNotExist:
            messages.error(request, "⚠️ Esse agendamento não pôde ser finalizado.")            

        return redirect("home")
