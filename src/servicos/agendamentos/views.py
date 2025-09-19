from datetime import date, timedelta

from django.views import View
from django.views.generic import CreateView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import Http404
from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404

from core.bases.views import BasePageView, BaseDynamicListView, BaseDynamicFormView, SelecaoDynamicListView, BaseDeleteView
from core.bases.mixins import AtivosQuerysetMixin, RedirecionarOrigemMixin
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


#Main
class PlanilhaDiariaView(LoginRequiredMixin, ContextoEmpresaMixin, BasePageView):
    template_name = "planilha-diaria.html"
    model = Agendamento
    data_proxima_nomes_display: dict[int, str] = {
        -2: "Anteontem",
        -1: "Ontem",
        0: "Hoje",
        1: "Amanhã",
        2: "Depois de amanhã"
    }

    def get_data_agendado_offset(self) -> tuple[date, int]:
        """
        Calcula a data de referência e a diferença de dias a partir do parâmetro da URL.
        Retorna uma tupla com (data_referencia, diferenca_dias).
        """
        diferenca_dias_str = self.kwargs.get("data_difference", None)

        if diferenca_dias_str is None:
            diferenca_dias = 0
        else:
            try:
                diferenca_dias = int(diferenca_dias_str)
            except ValueError:
                messages.warning(self.request, "⚠️ Parâmetro de data inválido. Mostrando agendamentos de hoje.")
                diferenca_dias = 0

        data_referencia = date.today() + timedelta(days=diferenca_dias)
        return data_referencia, diferenca_dias
    
    def get_data_referencia_display(self, diferenca_dias: int) -> str:
        data_display = self.data_proxima_nomes_display.get(diferenca_dias, None)

        if not data_display:
            if diferenca_dias < 0:
                data_display = f"Há {abs(diferenca_dias)} dias atrás"
            elif diferenca_dias > 0:
                data_display = f"Em {diferenca_dias} dias"
            else:
                # não deve chegar aqui, pois 0 está coberto no dict
                data_display = "Erro desconhecido"
        
        return data_display

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)

        data_referencia, diferenca_dias = self.get_data_agendado_offset()

        agendamentos_do_dia = self.model.objects.filter(
            empresa=self.request.empresa,
            data_agendado__date=data_referencia
        ).select_related(
            'cliente', 'servico', 'trabalhador'
        ).order_by("data_agendado")

        contexto["title"] = "Planilha Diária de Agendamentos"
        contexto["description"] = "Visualize seus agendamentos do dia a dia."

        # dict[list]
        contexto["agendamentos_fluxo_dict"] = {
            "pendente": agendamentos_do_dia.filter(status=AGENDAMENTO_STATUS_PENDENTE),
            "executando": agendamentos_do_dia.filter(status=AGENDAMENTO_STATUS_EXECUTANDO),
            "finalizado": agendamentos_do_dia.filter(status=AGENDAMENTO_STATUS_FINALIZADO),
            "cancelado": agendamentos_do_dia.filter(status=AGENDAMENTO_STATUS_CANCELADO)
        }

        contexto["data_referencia_display"] = self.get_data_referencia_display(diferenca_dias)
        contexto["data_referencia"] = data_referencia.strftime("%d/%m/%Y")
        contexto["dia_anterior_diff"] = diferenca_dias - 1
        contexto["dia_seguinte_diff"] = diferenca_dias + 1
        contexto["dia_anterior_diff_display"] = (data_referencia - timedelta(days=1)).strftime("%d/%m")
        contexto["dia_seguinte_diff_display"] = (data_referencia + timedelta(days=1)).strftime("%d/%m")

        contexto["urls_actions"] = {
            "last_status_url": 'servicos:agendamentos:last-status',
            "next_status_url": 'servicos:agendamentos:next-status',
        }
        
        return contexto

#* CRUD
class AgendamentoListView(AgendamentosSearchMixin, EscopoEmpresaQuerysetMixin, AtivosQuerysetMixin, BaseDynamicListView):
    model = Agendamento    

    def get_fields_display(self):
        return ['data_agendado', 'status', 'cliente', 'servico', 'trabalhador']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Lista de Agendamentos"
        return context


class AgendamentoCreateView(FormFieldsComEscopoEmpresaMixin, BaseDynamicFormView, RedirecionarOrigemMixin, CreateView):
    model = Agendamento
    form_class = AgendamentoForm
    success_url = reverse_lazy('servicos:agendamentos:list')

    def form_valid(self, form):
        messages.success(self.request, "✅ Agendamento registrado com sucesso!")  
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.warning(self.request, "⚠️ Não foi possível registrar o Agendamento!")  
        return super().form_invalid(form)


class BaseAgendamentoStatusUpdateView(LoginRequiredMixin, ContextoEmpresaMixin, RedirecionarOrigemMixin, View):
    model = Agendamento
    fields = ['status']
    success_url = reverse_lazy('servicos:agendamentos:list')

    def get_object(self):
        obj = get_object_or_404(self.model, pk=self.kwargs.get("pk"))
        if obj.empresa != self.request.empresa:
            raise Http404("Agendamento não encontrado ou você não tem permissão para acessá-lo.")
        return obj
    
    def adicionar_mensagem_sucesso(self, agendamento: Agendamento):
            messages.success(self.request, f"✅ Agendamento de {agendamento.cliente.nome} atualizado para {agendamento.get_status_display()}.")

    def post(self, request, *args, **kwargs):
        """
        Método post deve ser usado para modificar status de um agendamento.
        """
        raise NotImplementedError(f"Subclasses de {self.__class__.__name__} devem implementar o método post().")


class AtualizarOuAvancarStatusFluxoAgendamentoView(BaseAgendamentoStatusUpdateView):
    def post(self, request, *args, **kwargs):
        agendamento = self.get_object()

        status_requerido = request.POST.get("status")  # P, E, F, C...
        status_choice = next(
            (choice for choice, _ in C_TIPO_STATUS_AGENDAMENTO if choice == status_requerido),
            None
        )

        if status_choice:
            # Only set if status_choice exists
            agendamento.status = status_choice # type: ignore
            agendamento.save(update_fields=self.fields)
            self.adicionar_mensagem_sucesso(agendamento)
        elif status_requerido:
            # Se um status foi requerido mas não é válido
            messages.error(request, f"Status '{status_requerido}' é inválido.")
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
                    agendamento.save(update_fields=self.fields)
                    self.adicionar_mensagem_sucesso(agendamento)
                    break
            else:
                messages.warning(request, "⚠️ Agendamento já chegou no fim do ciclo.")

        return redirect(self.get_success_url())


class VoltarStatusFluxoAgendamentoView(BaseAgendamentoStatusUpdateView):
    def post(self, request, *args, **kwargs):
        agendamento = self.get_object()

        current_index = next(
            (i for i, (choice, _) in enumerate(C_TIPO_STATUS_AGENDAMENTO) if choice == agendamento.status),
            None
        )

        if current_index is None:
            raise Exception(f"Status atual '{agendamento.get_status_display()}' inválido.")

        # Find the previous non-cancelled status
        for index_anterior in range(current_index - 1, -1, -1):
            status_anterior = C_TIPO_STATUS_AGENDAMENTO[index_anterior][0]
            if status_anterior != AGENDAMENTO_STATUS_CANCELADO:
                agendamento.status = status_anterior
                agendamento.save(update_fields=self.fields)
                self.adicionar_mensagem_sucesso(agendamento)
                break
        else:
            messages.warning(request, "⚠️ Agendamento já chegou no início do ciclo.")

        return redirect(self.get_success_url())


#* Funcionalidades
class FinalizarAgendamentoView(LoginRequiredMixin, AgendamentosSearchMixin, EscopoEmpresaQuerysetMixin, RedirecionarOrigemMixin, SelecaoDynamicListView):
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
            agendamento.save(update_fields=['status'])
            messages.success(request, "✅ Agendamento finalizado com sucesso!")
        except Agendamento.DoesNotExist:
            messages.error(request, "⚠️ Esse agendamento não pôde ser finalizado.")            

        return redirect("home")


class AgendamentoDeleteView(LoginRequiredMixin, ContextoEmpresaMixin, BaseDeleteView):
    model = Agendamento
    success_url = reverse_lazy('servicos:agendamentos:list')