from core.bases.admin import BaseAssociadoEmpresaAdmin


class PessoaAdmin(BaseAssociadoEmpresaAdmin):
    search_fields = "nome", "cpf", "telefone", "endereco"
    search_help_text = "Nome, CPF, telefone ou endereço..."

    def get_list_display(self, request):
        base_list = list(super().get_list_display(request))

        new_list = ["nome", "cpf", "telefone", "endereco"]

        return new_list + base_list

    def get_fieldsets(self, request, obj = ...):
        base_fieldsets = list(super().get_fieldsets(request, obj))
        
        new_fieldsets = [
            (
                "Basic",
                {
                    'fields': ('nome', 'cpf', 'imagem')
                }
            ),
            (
                "Additional",
                {
                    'classes': ('collapse', ),
                    'fields': ('telefone', 'endereco', 'ativo')
                }
            )
        ]

        return base_fieldsets + new_fieldsets
