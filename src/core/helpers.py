
import locale
    
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

class ConversionHelper:
    @staticmethod
    def formatar_moeda(value: float | int) -> str:
        """Formata um valor numérico para a moeda brasileira (BRL)."""        
        return locale.currency(value or 0.0, grouping=True, symbol=True)
