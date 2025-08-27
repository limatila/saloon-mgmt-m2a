from django.db import models

from core.bases.models import BaseAssociadoEmpresa
from servicos.agendamentos.choices import C_TIPO_STATUS_AGENDAMENTO, AGENDAMENTO_STATUS_PENDENTE


class Agendamento(BaseAssociadoEmpresa):
    data_agendado = models.DateTimeField(
        verbose_name="Data Agendado",
        null=False,
        blank=False
    )
    status = models.CharField(
        verbose_name="Status",
        choices=C_TIPO_STATUS_AGENDAMENTO,
        default=AGENDAMENTO_STATUS_PENDENTE,
        max_length=1,
        null=False,
        blank=False
    )

    #FKs
    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        verbose_name="Cliente",
        null=False
    )
    servico = models.ForeignKey(
        'tipo_servicos.TipoServico',
        on_delete=models.PROTECT,
        verbose_name="Serviço contratado",
        null=False
    )
    trabalhador = models.ForeignKey(
        'trabalhadores.Trabalhador',
        on_delete=models.PROTECT,
        verbose_name="Trabalhador",
        null=False
    )

    def __str__(self):
        return f"{self.cliente.nome}, {self.servico.nome} at {self.data_agendado.date()}"
