from marshmallow import ValidationError
from helpers.database import db
from datetime import date

def validar_unique_cpf(value):
    from models.TB_Responsavel import TB_Responsavel
    if db.session.query(TB_Responsavel).filter_by(responsavel_cpf=value).first():
        raise ValidationError(
            "Já existe um Responsavel cadastrado com esse CPF."
        )

def validar_unique_siap(value):
    from models.TB_Responsavel import TB_Responsavel
    if db.session.query(TB_Responsavel).filter_by(responsavel_siap=value).first():
        raise ValidationError(
            "Já existe um Responsavel cadastrado com esse SIAP."
        )
    

def validarIdade(data_nascimento):
    hoje = date.today()

    idade = hoje.year - data_nascimento.year

    if (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day):
        idade -= 1

    if idade < 12 or idade > 80:
        raise ValidationError(
            "A idade deve estar entre 12 e 80 anos."
        )