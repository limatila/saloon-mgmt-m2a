from django.views import View
from django.views.generic import CreateView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404

from core.bases.views import BaseDynamicListView, BaseDynamicFormView, SelecaoDynamicListView, BaseDeleteView
from core.bases.mixins import AtivosQuerysetMixin
from cadastros.empresas.mixins import EscopoEmpresaQuerysetMixin, ContextoEmpresaMixin, FormFieldsComEscopoEmpresaMixin
from servicos.agendamentos.models import Agendamento
from servicos.agendamentos.forms import AgendamentoForm
from servicos.agendamentos.mixins import AgendamentosSearchMixin
from servicos.agendamentos.choices import (
    AGENDAMENTO_STATUS_CANCELADO,
    C_TIPO_STATUS_AGENDAMENTO,
    AGENDAMENTO_STATUS_PENDENTE,
    AGENDAMENTO_STATUS_EXECUTANDO,
    AGENDAMENTO_STATUS_FINALIZADO 
)


class AgendamentoListView(AgendamentosSearchMixin, EscopoEmpresaQuerysetMixin, AtivosQuerysetMixin, BaseDynamicListView):
    model = Agendamento

    def get_fields_display(self):
        return ['data_agendado', 'status', 'cliente', 'servico', 'trabalhador']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Lista de Agendamentos"
        return context


class AgendamentoCreateView(FormFieldsComEscopoEmpresaMixin, BaseDynamicFormView, CreateView):
    model = Agendamento
    form_class = AgendamentoForm
    success_url = reverse_lazy('servicos:agendamentos:list')

    def form_valid(self, form):
        messages.success(self.request, "✅ Agendamento registrado com sucesso!")  
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "⚠️ Não foi possível registrar o Agendamento!")  
        return super().form_invalid(form)


class AtualizarStatusFluxoAgendamentoView(LoginRequiredMixin, ContextoEmpresaMixin, View):
    model = Agendamento
    fields = ['status']
    success_url = reverse_lazy('servicos:agendamentos:list')

    def get_object(self):
        return get_object_or_404(self.model, pk=self.kwargs["pk"])
    
    def post(self, request, *args, **kwargs):
        agendamento = self.get_object()

        status_requerido = request.POST.get("status")  # P, E, F, C...
        status_choice = next(
            (choice for choice, _ in C_TIPO_STATUS_AGENDAMENTO if choice == status_requerido),
            None
        )

        if status_choice:
            # Only set if status_choice exists
            agendamento.status = status_choice
            agendamento.save()
            messages.success(request, f"✅ Status atualizado para {agendamento.get_status_display()}.")

        else:
            # Auto-advance to the next valid status
            current_index = next(
                (i for i, (choice, _) in enumerate(C_TIPO_STATUS_AGENDAMENTO) if choice == agendamento.status),
                None
            )

            if current_index is None:
                raise Exception(f"Status atual '{agendamento.get_status_display()}' inválido.")

            # Find the next non-cancelled status
            for next_index in range(current_index + 1, len(C_TIPO_STATUS_AGENDAMENTO)):
                next_status = C_TIPO_STATUS_AGENDAMENTO[next_index][0]
                if next_status != AGENDAMENTO_STATUS_CANCELADO:
                    agendamento.status = next_status
                    agendamento.save()
                    break
            else:
                messages.warning(request, "⚠️ Agendamento já chegou no fim do ciclo.")

        return redirect(self.success_url)


#* Funcionalidades
class FinalizarAgendamentoView(LoginRequiredMixin, AgendamentosSearchMixin, EscopoEmpresaQuerysetMixin, SelecaoDynamicListView):
    model = Agendamento
    condicao_agendamento_valido = (
        Q(status=AGENDAMENTO_STATUS_PENDENTE) | Q(status=AGENDAMENTO_STATUS_EXECUTANDO)
    )

    def get_queryset(self):
        contexto = super().get_queryset()
        contexto = contexto.filter(self.condicao_agendamento_valido)
        return contexto

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


class AgendamentoDeleteView(LoginRequiredMixin, ContextoEmpresaMixin, BaseDeleteView):
    model = Agendamento
    success_url = reverse_lazy('servicos:agendamentos:list')