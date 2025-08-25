from django.db import models

from core.models import Base
from servicos.choices import C_TIPO_STATUS_AGENDAMENTO, AGENDAMENTO_STATUS_PENDENTE

# Create your models here.
class Agendamento(Base):
    data_agendado = models.DateField(
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
        'cadastros.Cliente',
        on_delete=models.PROTECT,
        verbose_name="Cliente",
        null=False
    )
    servico = models.ForeignKey(
        'cadastros.Servico',
        on_delete=models.PROTECT,
        verbose_name="Serviço contratado",
        null=False
    )
    trabalhador = models.ForeignKey(
        'cadastros.Trabalhador',
        on_delete=models.PROTECT,
        verbose_name="Trabalhador",
        null=False
    )

    def __str__(self):
        return f"{self.client.name} at {self.date_scheduled.date()}"
