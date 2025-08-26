from django.db import models

from core.models import Base, Pessoa

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

class Trabalhador(Pessoa):
    class Meta:
        verbose_name_plural = "Trabalhadores"

class Servico(Base):
    nome = models.CharField(
        verbose_name="Nome do serviço",
        max_length=50,
        null=False,
        blank=False
    )
    preco = models.DecimalField(
        verbose_name="Preço",
        max_digits=12,
        decimal_places=2,
    )

    def __str__(self):
        return f"{self.nome} por R${self.preco}"