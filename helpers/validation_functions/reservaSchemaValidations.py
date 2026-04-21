from marshmallow import Schema, fields, validate, ValidationError, validates, validates_schema
from datetime import date, datetime


erros_possiveis = {
    "required":"O campo {campo} é obrigatório.",
    "null":"O campo {campo} não pode ser nulo.",
    "validator_failed":"O campo {campo} deve ser valido (Maior que 0) e Corresponder a um {campo} existente.",
    "invalid":"Formato inválido para {campo}."
    }

def montarMensagemDeErro(nomeDoCampo, listaDeTiposDeErros, horaOuData=None):
    resposta = {}

    for erro in listaDeTiposDeErros:
        if erro in erros_possiveis:
            if nomeDoCampo == "dias_semana":
                if erro == "invalid":
                    mensagem = f"{nomeDoCampo} inválido, tente valores entre 1 e 7."
            else:
                mensagem = erros_possiveis[erro].format(campo=nomeDoCampo)

            if horaOuData:
                if horaOuData == "h":
                    mensagem += f" Use HH:MM."
                else:
                    mensagem += f" Use YYYY-MM-DD."

            resposta[erro] = mensagem

    return resposta

def validateReservaRules(data):
    data_inicio = data.get("data_inicio")
    data_fim = data.get("data_fim")
    hora_inicio = data.get("hora_inicio")
    hora_fim = data.get("hora_fim")
    frequencia = data.get("frequencia")
    dias_semana = data.get("dias_semana", [])

    hoje = date.today()
    agora = datetime.now().time()

    if frequencia == "única":
        if data_fim and data_inicio and data_fim != data_inicio:
            raise ValidationError({
                "data_fim": "Em um reserva única data_fim não pode ser diferente de data_inicio."
            })
    
    if data_inicio and data_inicio < hoje:
        raise ValidationError({
            "data_inicio": "data_inicio não pode ser uma data passada."
        })

    if data_inicio and hora_inicio and data_inicio == hoje and hora_inicio <= agora:
        raise ValidationError({
            "hora_inicio": "hora_inicio não pode ser um horário passado."
        })

    if hora_inicio and hora_fim and hora_fim <= hora_inicio:
        raise ValidationError({
            "hora_fim": "hora_fim deve ser maior que hora_inicio."
        })

    if data_inicio and data_fim and data_fim < data_inicio:
        raise ValidationError({
            "data_fim": "data_fim deve ser maior ou igual a data_inicio."
        })


    if frequencia not in ("única", "mensal"):
        if not dias_semana:
            raise ValidationError({
                "dias_semana": (
                    "Esta frequência exige a informação de dias_semana."
                )
            })

        if data_inicio:
            dia_real = data_inicio.weekday() + 1  # 1=segunda ... 7=domingo

            if dia_real not in dias_semana:
                raise ValidationError({
                    "dias_semana": (
                        f"data_inicio ({data_inicio}) corresponde ao dia "
                        f"{dia_real}, que não está em dias_semana."
                    )
                })
