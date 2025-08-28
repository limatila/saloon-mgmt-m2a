from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView 
from django.views.generic import CreateView, ListView, UpdateView #DeleteView não recomendado, apenas inativar o registro.

class BaseView(TemplateView):
    template_name = "base.html"

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto["title"] = "Base"
        contexto["nome"] = "atila"
        return contexto
    