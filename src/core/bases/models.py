from django.db import models


class BaseModel(models.Model):
    data_criado = models.DateTimeField(
        verbose_name="Data de Criação",
        auto_now_add=True,
        null=False,
        blank=False
    )
    data_modificado = models.DateTimeField(
        verbose_name="Data de Modificação",
        auto_now=True,
        null=False,
        blank=False
    )
    ativo = models.BooleanField(
        verbose_name="Ativo",
        default=True,
        null=False,
        blank=False
    )

    def __str__(self):
        return f"{self.id} - {self.nome}"

    class Meta:
        abstract = True
