from django.db import models

from cadastros.models import BaseCadastrosModel


class TipoServico(BaseCadastrosModel):
    nome = models.CharField(
        verbose_name="Nome do serviço",
        max_length=50,
        null=False,
        blank=False
    )
    preco = models.DecimalField(
        verbose_name="Preço",
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.nome} por R${self.preco}"
