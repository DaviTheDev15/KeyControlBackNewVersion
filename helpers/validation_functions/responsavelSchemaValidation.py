from marshmallow import ValidationError
from models.TB_Responsavel import TB_Responsavel
from helpers.database import db

def validar_unique_cpf(value):
    if db.session.query(TB_Responsavel).filter_by(responsavel_cpf=value).first():
        raise ValidationError(
            "Já existe um Responsavel cadastrado com esse CPF."
        )

def validar_unique_siap(value):
    if db.session.query(TB_Responsavel).filter_by(responsavel_siap=value).first():
        raise ValidationError(
            "Já existe um Responsavel cadastrado com esse SIAP."
        )