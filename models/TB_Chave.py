from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, ForeignKey
from helpers.database import db
from marshmallow import Schema, fields
from flask_restful import fields as flaskFields
from helpers.validation_functions.genericValidations import validate_positive, montarDicionarioDeMensagemDeErro

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

    chave_nome = fields.Str(dump_only=True)
    
    sala_id = fields.Int(
        required=True,
        validate=validate_positive,
        error_messages=montarDicionarioDeMensagemDeErro("sala_id",["required", "null", "validator_failed"]))

    disponivel = fields.Boolean(
        required=True,
        error_messages=montarDicionarioDeMensagemDeErro("disponivel", ["required", "invalid"], "b"))