from random import choice, random

from django.core.management.base import BaseCommand
from faker import Faker
from validate_docbr import CPF

from cadastros.clientes.models import Cliente
from cadastros.tipo_servicos.models import TipoServico
from cadastros.trabalhadores.models import Trabalhador
from cadastros.empresas.models import Empresa
from servicos.agendamentos.models import Agendamento, C_TIPO_STATUS_AGENDAMENTO


class Command(BaseCommand):
    help = "Cria dados aleatórios no banco de dados"

    def handle(self, *args, **kwargs):
        fake = Faker()
        cpf = CPF()
        #cria manualmente objetos de model empresa
        additions = [
            Cliente(
                nome=fake.name(),
                cpf=cpf.generate(),
                telefone=fake.phone_number(),
                endereco=fake.address()
            ),
            TipoServico(
                nome=f"{choice(['Corte', 'Limpeza', 'Hidratação'])}" + f" {choice(['Simples', 'Complexo', 'Completo', 'Barba'])}",
                preco=random() * 100
            ),
            Trabalhador(
                nome=fake.name(),
                cpf=cpf.generate()
            ),
        ]
        novo_agendamento = Agendamento(
            data_agendado=fake.future_datetime(),
            status=choice(C_TIPO_STATUS_AGENDAMENTO)[0],
            cliente=additions[0],
            servico=additions[1],
            trabalhador=additions[2]
        )
        additions.append(novo_agendamento)

        #insere no banco
        for addition in additions:
            try:
                print("salvando " + repr(addition))
                addition.save()
            except Exception as err:
                print("não salvou")
                print(err)
                pass