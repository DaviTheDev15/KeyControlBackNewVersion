from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, DateTime, func
from helpers.database import db
from helpers.validation_functions.genericValidations import montarDicionarioDeMensagemDeErro
from marshmallow import Schema, fields, validate, validates
from flask_restful import fields as flaskFields
from datetime import datetime

tb_sala_fields = {
    'sala_id': flaskFields.Integer,
    'sala_nome': flaskFields.String,
    'disponivel': flaskFields.Boolean,
    'created_at': flaskFields.DateTime,
    'deleted_at': flaskFields.DateTime
}

class TB_Sala(db.Model):
    __tablename__ = "tb_sala"

    sala_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sala_nome: Mapped[str] = mapped_column(String(255), nullable=False)
    disponivel: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    tb_chave = relationship("TB_Chave", back_populates="tb_sala")
    tb_reserva = relationship("TB_Reserva", back_populates="tb_sala")


class TB_SalaSchema(Schema):
    sala_id = fields.Int(dump_only=True)
    
    sala_nome = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=255, error="O campo sala_nome deve ter entre 2 a 255 caracteres."),
        error_messages=montarDicionarioDeMensagemDeErro("sala_nome", ["required", "null"]))
    
    disponivel = fields.Boolean(
        required=True,
        error_messages=montarDicionarioDeMensagemDeErro("disponivel", ["required", "invalid"]))
    
    created_at = fields.DateTime(
        required=True,
        error_messages=montarDicionarioDeMensagemDeErro("created_at",["required", "null"])
    )