from django.db import models

# Create your models here.
# Classes Abstratas
class Base(models.Model):
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

    class Meta:
        abstract = True

class Pessoa(Base):
    nome = models.CharField(
        null=False,
        blank=False,
    )
    cpf = models.CharField(
        verbose_name="CPF",
        null=False,
        blank=False,
        max_length=11,
        unique=True
    )
    ativo = models.BooleanField(
        default=True,
        null=False,
        blank=False
    )
    image = models.ImageField(
        default="placeholder.jpg",
        upload_to="imagens-pessoas/",
        null=True,
        blank=True,
        editable=True,
    )

    def __str__(self):
        return f"{self.id} - {self.name}"

    class Meta:
        abstract = True

# Classes Concretas
class Cliente(Pessoa):
    telefone = models.CharField(
        max_length=21,
        null=False,
        blank=False,
        unique=True
    )

class Servico(Base):
    class TipoServico(models.TextChoices):
        PENDENTE = 'P', "Pendente"
        EXECUTANDO =  'E', "Executando"
        FINALIZADO = 'F', "Finalizado"
        CANCELADO = 'C', "Cancelado"

    nome = models.CharField(
        verbose_name="Nome do serviço",
        max_length=50,
        null=False,
        blank=False
    )
    preco = models.DecimalField(
        verbose_name="Preço"
    )

class Trabalhador(Pessoa):
    ...

class Agendamento(Base):
    data_agendado = models.DateField(
        null=False,
        blank=False
    )

    cliente = models.ForeignKey(
        'Cliente',
        on_delete=models.PROTECT,
        verbose_name="Cliente",
        null=False
    )
    servico = models.ForeignKey(
        'Servico',
        on_delete=models.PROTECT,
        verbose_name="Serviço contratado",
        null=False
    )
    trabalhador = models.ForeignKey(
        'Trabalhador',
        on_delete=models.PROTECT,
        verbose_name="Trabalhador",
        null=False
    )

    def __str__(self):
        return f"{self.client.name} at {self.date_scheduled.date()}"