from cadastros.models import models, Pessoa


# Create your models here.
class Cliente(Pessoa):
    telefone = models.CharField(
        max_length=21,
        null=False,
        blank=False,
        unique=True
    )
    endereco = models.CharField(
        verbose_name="Endereço",
        null=False,
        blank=False
    )