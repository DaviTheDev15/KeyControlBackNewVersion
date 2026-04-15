from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean
from helpers.database import db
from marshmallow import Schema, fields, validate, ValidationError, validates
from flask_restful import fields as flaskFields

tb_sala_fields = {
    'sala_id': flaskFields.Integer,
    'sala_nome': flaskFields.String,
    'disponivel': flaskFields.Boolean
}

class TB_Sala(db.Model):
    __tablename__ = "tb_sala"

    sala_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sala_nome: Mapped[str] = mapped_column(String(255), nullable=False)
    disponivel: Mapped[bool] = mapped_column(Boolean, nullable=False)

    tb_chave = relationship("TB_Chave", back_populates="tb_sala")
    tb_reserva = relationship("TB_Reserva", back_populates="tb_sala")


class TB_SalaSchema(Schema):
    sala_id = fields.Int(dump_only=True)
    
    sala_nome = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=255),
        error_messages={"required": "O campo sala_nome é obrigatório.", 
            "null": "O campo sala_nome não pode ser nulo.", 
            "validator_failed": "O campo sala_nome deve ter entre 2 a 255 caracteres."})
    
    disponivel = fields.Boolean(
        required=True,
        error_messages={
            "required":"O campo disponivel é obrigatório.",
            "invalid":"O campo ativo aceita apenas valores booleanos(False e True)."
        }
    )