from django.db import models

from cadastros.empresas.models import BaseAssociadoEmpresa
from servicos.agendamentos.choices import C_TIPO_STATUS_AGENDAMENTO, AGENDAMENTO_STATUS_PENDENTE


class Agendamento(BaseAssociadoEmpresa):
    data_agendado = models.DateTimeField(
        verbose_name="Data Agendado",
        null=False,
        blank=False
    )
    status = models.CharField(
        verbose_name="Estado",
        choices=C_TIPO_STATUS_AGENDAMENTO,
        default=AGENDAMENTO_STATUS_PENDENTE,
        max_length=1,
        null=False,
        blank=False
    )

    #FKs
    cliente = models.ForeignKey(
        'clientes.Cliente',
        verbose_name="Cliente",
        on_delete=models.PROTECT,
        null=False
    )
    servico = models.ForeignKey(
        'tipo_servicos.TipoServico',
        verbose_name="Serviço contratado",
        on_delete=models.PROTECT,
        null=False
    )
    trabalhador = models.ForeignKey(
        'trabalhadores.Trabalhador',
        verbose_name="Trabalhador",
        on_delete=models.PROTECT,
        null=False
    )

    def __str__(self):
        return f"{self.cliente.nome}, {self.servico.nome} at {self.data_agendado.date()}"
