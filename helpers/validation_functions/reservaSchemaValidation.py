from marshmallow import ValidationError
from helpers.validation_functions.genericValidations import montarDicionarioDeMensagemDeErro
from datetime import date

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
            raise ValidationError(montarDicionarioDeMensagemDeErro("frequencia", "frequencia_data_fim"))
        
    if frequencia not in ("única", "mensal"):
        if not dias_semana:
            raise ValidationError(montarDicionarioDeMensagemDeErro("frequencia", "frequencia_semanal_quinzenal_dias_semana"))
        
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
    dias_semana = data.get("dias_semana", [])
    hoje = date.today()

    if data_inicio < hoje:
        raise ValidationError(montarDicionarioDeMensagemDeErro("data_inicio", "data_inicio"))
    
    if data_fim < data_inicio:
        raise ValidationError(montarDicionarioDeMensagemDeErro("data_fim", "data_fim"))
    
    
def validarHoras(data):
    hora_inicio = data.get("hora_inicio")
    hora_fim = data.get("hora_fim")
    #data_inicio = data.get("data_inicio")
    #hoje = date.today()
    #agora = datetime.now().time()

    if hora_fim <= hora_inicio:
        raise ValidationError(montarDicionarioDeMensagemDeErro("hora_fim", "hora_fim"))
    
    '''if data_inicio and hora_inicio == hoje and hora_inicio <= agora:
        raise ValidationError(montarMensagemDeErro("hora_inicio", "hora_inicio"))'''
