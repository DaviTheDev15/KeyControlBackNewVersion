from marshmallow import ValidationError
from flask_restful import fields as flaskFields
from helpers.validation_functions.possibleValidationErrors import erros_possiveis

class DateFormat(flaskFields.Raw):
    def format(self, value):
        return value.isoformat() if value else None
    
class TimeFormat(flaskFields.Raw):
    def format(self, value):
        return value.strftime("%H:%M") if value else None

class DiasReservaField(flaskFields.Raw):
    def format(self, value):
        return [d.dia_semana for d in value] 


def validate_positive(value):
    if value <= 0:
        raise ValidationError("O valor deve ser um número inteiro não negativo.")
    
def montarDicionarioDeMensagemDeErro(nomeDoCampo, listaDeTiposDeErros, excecao=None):
    if not isinstance(listaDeTiposDeErros, (list, tuple, set)):
        listaDeTiposDeErros = [listaDeTiposDeErros]
    
    resposta = {}

    for erro in listaDeTiposDeErros:
        if erro in erros_possiveis:
            mensagem = erros_possiveis[erro].format(campo=nomeDoCampo)

            if excecao and erro == "invalid":
                excecao = excecao.lower()
                if excecao[0] == "h":
                    mensagem += f" Use HH:MM."
                elif excecao[0] == "y":
                    mensagem += f" Use YYYY-MM-DD."
                elif excecao[0] == "b":
                    mensagem += f" Use apenas valores booleanos False ou True."

            resposta[erro] = mensagem

    return resposta
