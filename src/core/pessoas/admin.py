from core.bases.admin import BaseAssociadoEmpresaAdmin


class PessoaAdmin(BaseAssociadoEmpresaAdmin):
    search_fields = "nome", "cpf", "telefone", "endereco"
    search_help_text = "Nome, CPF, telefone ou endereço..."

    def get_fieldsets(self, request, obj = ...):
        base_fieldsets = list(super().get_fieldsets(request, obj))
        
        new_fieldsets = [
            (
                "Basic",
                {
                    'fields': ('nome', 'cpf')
                }
            ),
            (
                "Additional",
                {
                    'classes': ('collapse', ),
                    'fields': ('telefone', 'endereco')
                }
            )
        ]

        return base_fieldsets + new_fieldsets
