from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, ForeignKey
from helpers.database import db
from marshmallow import Schema, fields, validate, ValidationError, validates
from flask_restful import fields as flaskFields

def validate_positive(value):
    if value <= 0:
        raise ValidationError("O valor deve ser um número inteiro não negativo.")

tb_chave_fields = {
    'chave_id': flaskFields.Integer,
    'chave_nome': flaskFields.String,
    'sala_id': flaskFields.Integer,
    'disponivel': flaskFields.Boolean
}

class TB_Chave(db.Model):
    __tablename__ = "tb_chave"

    chave_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chave_nome: Mapped[str] = mapped_column(String(255), nullable=False)
    sala_id: Mapped[int] = mapped_column(Integer, ForeignKey('tb_sala.sala_id'), nullable=False)
    disponivel: Mapped[bool] = mapped_column(Boolean, nullable=False)

    tb_sala = relationship("TB_Sala", back_populates="tb_chave")

    tb_retirada = relationship("TB_Retirada", back_populates="tb_chave")


class TB_ChaveSchema(Schema):
    chave_id = fields.Int(dump_only=True)

    chave_nome = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=255),
        error_messages={"required":"O campo chave_nome é obrigatório.",
        "null":"O campo chave_nome não pode ser nulo.", 
        "validator_failed":"O campo chave_nome deve ter entre 2 a 255 caracteres."})
    
    sala_id = fields.Int(
        required=True,
        validate=validate_positive,
        error_messages={
            "required": "O campo sala_id é obrigatório.",
            "null": "O campo sala_id não pode ser nulo.",
            "validator_failed": "O campo sala_id deve ser valido(Maior que 0) e Corresponder a uma sala existente."
        })
    
    disponivel = fields.Boolean(
        required=True,
        error_messages={
            "required":"O campo disponivel é obrigatório.",
            "invalid":"O campo ativo aceita apenas valores booleanos(False e True)."
        })