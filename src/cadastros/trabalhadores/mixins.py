
from core.bases.mixins import BaseViewComTableOptionsMixin


class TrabalhadoresTableOptionsMixin(BaseViewComTableOptionsMixin):
    #! finish all links
    def get_options_modal(self):
        return [
            {
                'nome': "Detalhar",
                'description': "ver em detalhe",
                'fa_icon': "circle-info",
                'link_module': 'cadastros:trabalhadores:detail'
            },
            {
                'nome': 'Deletar',
                'description': 'remova esse registro',
                'fa_icon': 'circle-minus',
                'link_module': 'cadastros:trabalhadores:delete'
            },
            {
                'nome': 'Histórico',
                'description': 'histórico de ações',
                'fa_icon': 'circle-minus',
                'link_module': 'cadastros:trabalhadores:history'
            }
        ]