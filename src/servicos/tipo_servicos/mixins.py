
from core.bases.mixins import BaseViewComTableOptionsMixin


class TipoServicoTableOptionsMixin(BaseViewComTableOptionsMixin):
    #! finish all links
    def get_options_modal(self):
        return [
            {
                'nome': "Detalhar",
                'description': "ver em detalhe",
                'fa_icon': "circle-info",
                'link_module': 'cadastros:tipo_servicos:detail'
            },
            {
                'nome': 'Adicionar Com Serviço',
                'description': 'adicione um agendamento com esse serviço',
                'fa_icon': 'pencil',
                'link_module': 'cadastros:tipo_servicos:edit'
            },
            {
                'nome': 'Deletar',
                'description': 'remova esse registro',
                'fa_icon': 'circle-minus',
                'link_module': 'cadastros:tipo_servicos:delete'
            },
            {
                'nome': 'Histórico',
                'description': 'histórico de ações',
                'fa_icon': 'circle-minus',
                'link_module': 'cadastros:tipo_servicos:historic'
            }
        ]