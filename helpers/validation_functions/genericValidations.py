from marshmallow import ValidationError
from flask_restful import fields as flaskFields
from datetime import date

class DateFormat(flaskFields.Raw):
    def format(self, value):
        return value.isoformat() if value else None
    
class TimeFormat(flaskFields.Raw):
    def format(self, value):
        return value.strftime("%H:%M") if value else None

class DiasReservaField(flaskFields.Raw):
    def format(self, value):
        return [d.dia_semana for d in value] 

erros_possiveis = {
    "required":"O campo {campo} é obrigatório.",
    "null":"O campo {campo} não pode ser nulo.",
    "validator_failed":"O campo {campo} deve ser valido (Maior que 0) e Corresponder a um {campo} existente.",
    "invalid":"Formato inválido para {campo}."
    }

def validate_positive(value):
    if value <= 0:
        raise ValidationError("O valor deve ser um número inteiro não negativo.")
    
def montarMensagemDeErro(nomeDoCampo, listaDeTiposDeErros, excecao=None):
    if not isinstance(listaDeTiposDeErros, (list, tuple, set)):
        listaDeTiposDeErros = [listaDeTiposDeErros]
    
    resposta = {}

    for erro in listaDeTiposDeErros:
        if erro in erros_possiveis:
            mensagem = erros_possiveis[erro].format(campo=nomeDoCampo)

            if excecao:
                excecao = excecao.lower()
                if excecao[0] == "h":
                    mensagem += f" Use HH:MM."
                elif excecao[0] == "y":
                    mensagem += f" Use YYYY-MM-DD."
                elif excecao[0] == "b":
                    mensagem += f" Use apenas valores booleanos False ou True."

            resposta[erro] = mensagem

    return resposta

def validateReservaRules(data):
    validarFrequencia(data)
    validarData(data)
    validarHoras(data)


def validarFrequencia(data):
    frequencia = data.get("frequencia")
    data_inicio = data.get("data_inicio")
    data_fim = data.get("data_fim")
    dias_semana = data.get("dias_semana", [])

    if frequencia == "única":
        if data_fim != data_inicio:
            raise ValidationError({
                "data_fim": "Em um reserva única data_fim não pode ser diferente de data_inicio."
            })
        
    if frequencia not in ("única", "mensal"):
        if not dias_semana:
            raise ValidationError({
                "dias_semana": (
                    "Esta frequência exige a informação de dias_semana."
                )
            })

        if data_inicio:
            dia_real = data_inicio.weekday() + 1

            if dia_real not in dias_semana:
                raise ValidationError({
                    "dias_semana": (
                        f"data_inicio ({data_inicio}) corresponde ao dia "
                        f"{dia_real}, que não está em dias_semana."
                    )
                })

def validarData(data):
    data_inicio = data.get("data_inicio")
    data_fim = data.get("data_fim")
    hoje = date.today()

    if data_inicio < hoje:
        raise ValidationError({
            "data_inicio": "data_inicio não pode ser uma data passada."
        })
    
    if data_fim < data_inicio:
        raise ValidationError({
            "data_fim": "data_fim deve ser maior ou igual a data_inicio."
        })
    
def validarHoras(data):
    hora_inicio = data.get("hora_inicio")
    hora_fim = data.get("hora_fim")
    #data_inicio = data.get("data_inicio")
    #hoje = date.today()
    #agora = datetime.now().time()

    if hora_fim <= hora_inicio:
        raise ValidationError({
            "hora_fim": "hora_fim deve ser maior que hora_inicio."
        })
    
    '''if data_inicio and hora_inicio == hoje and hora_inicio <= agora:
        raise ValidationError({
            "hora_inicio": "hora_inicio não pode ser um horário passado."
        })'''
