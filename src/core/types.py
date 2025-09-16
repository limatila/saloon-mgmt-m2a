# core/dashboard.py
from dataclasses import dataclass


@dataclass
class QuickInfoItem:
    header: str
    value: str
    conclusion: str
    fa_icon: str
    link_module: str


@dataclass
class QuickActionItem:
    header: str
    description: str
    fa_icon: str
    link_module: str


@dataclass
class TableOptionItemModal:
    nome: str
    description: str
    fa_icon: str
    link_module: str