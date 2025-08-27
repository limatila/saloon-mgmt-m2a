from cadastros.models import models, Pessoa


class Trabalhador(Pessoa):
    telefone = models.CharField(
        max_length=21,
        null=True,
        unique=True
    )
    class Meta:
        verbose_name_plural = "Trabalhadores"