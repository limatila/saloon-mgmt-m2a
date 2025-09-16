from dataclasses import dataclass


@dataclass
class RelatorioAcesso:
    nome: str
    url: str

@dataclass
class RelatorioGrupo:
    nome: str
    relatorios: list[RelatorioAcesso]