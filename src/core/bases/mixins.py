
class FormComArquivoMixin:
    """
    Inclui também os arquivos (FILES) no form.
    """
    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['form_with_file'] = True
        return contexto

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            "files": self.request.FILES or None
        })
        return kwargs

#? base security
