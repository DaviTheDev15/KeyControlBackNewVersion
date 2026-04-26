from marshmallow import ValidationError
from helpers.validation_functions.genericValidations import montarDicionarioDeMensagemDeErro
from datetime import date, datetime, timedelta
from flask import request

def validateRetiradaRules(self, data):
    validarStatus(self, data)
    validarData(data)
    validarHora(self, data)

def validarStatus(self,data):
    if request.method == "POST":
        if data.get("status") != "retirada":
            raise ValidationError(montarDicionarioDeMensagemDeErro("status", "status"))

def validarData(data):
    data_retirada = data.get("data_retirada")
    hoje = date.today()

    if data_retirada != hoje:
        raise ValidationError(montarDicionarioDeMensagemDeErro("data_retirada", "data_retirada"))
    
def validarHora(self, data):
    data_retirada = data.get("data_retirada")
    hora_retirada = data.get("hora_retirada")
    hora_prevista = data.get("hora_prevista_devolucao")
    hora_devolucao = data.get("hora_devolucao")
    status = data.get("status")
    hoje = date.today()
    agora = datetime.now()
    tolerancia = agora - timedelta(minutes=5)

    #if data_retirada == hoje and hora_retirada:
    if data_retirada:
        if data_retirada == hoje:
            retirada_dt = datetime.combine(hoje, hora_retirada)
            if retirada_dt < tolerancia:
                raise ValidationError(montarDicionarioDeMensagemDeErro("hora_retirada", "hora_retirada"))

    if hora_prevista <= hora_retirada:
        raise ValidationError(montarDicionarioDeMensagemDeErro("hora_prevista_devolucao", "hora_prevista_devolucao"))

    #if hora_devolucao and hora_retirada and hora_devolucao < hora_retirada:
    if hora_devolucao:
        if hora_devolucao < hora_retirada:
            raise ValidationError(montarDicionarioDeMensagemDeErro("hora_devolucao", "hora_devolucao"))


    if not self.partial and hora_devolucao:
        raise ValidationError(montarDicionarioDeMensagemDeErro("hora_devolucao", "post_hora_devolucao"))

    if status == "devolvida" and not hora_devolucao:
        raise ValidationError(montarDicionarioDeMensagemDeErro("hora_devolucao", "not_hora_devolucao_devolvida"))

    if status != "devolvida" and hora_devolucao:
        raise ValidationError(montarDicionarioDeMensagemDeErro("hora_devolucao","hora_devolucao_devolvida"))

