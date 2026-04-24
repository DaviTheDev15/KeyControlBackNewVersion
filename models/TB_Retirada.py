from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Date, Time, String, ForeignKey
from helpers.database import db
from marshmallow import Schema, fields, validate, ValidationError, validates, validates_schema
from flask_restful import fields as flaskFields
from datetime import date, datetime, timedelta

from helpers.validation_functions.genericValidations import DateFormat, TimeFormat, validate_positive, montarDicionarioDeMensagemDeErro
from helpers.validation_functions.retiradaSchemaValidation import validateRetiradaRules

tb_retirada_fields = {
    "retirada_id": flaskFields.Integer,
    "chave_id": flaskFields.Integer,
    "responsavel_id":flaskFields.Integer,
    "reserva_id":flaskFields.Integer,
    "data_retirada":DateFormat,
    "hora_retirada":TimeFormat,
    "hora_prevista_devolucao":TimeFormat,
    "hora_devolucao":TimeFormat,
    "status": flaskFields.String # retirada | devolvida | atrasada
}
    
class TB_Retirada(db.Model):
    __tablename__ = "tb_retirada"

    retirada_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chave_id: Mapped[int] = mapped_column(Integer, ForeignKey("tb_chave.chave_id"), nullable=False)
    responsavel_id: Mapped[int] = mapped_column(Integer, ForeignKey("tb_responsavel.responsavel_id"), nullable=False)
    reserva_id: Mapped[int] = mapped_column(Integer, ForeignKey("tb_reserva.reserva_id"), nullable=True)
    data_retirada: Mapped[Date] = mapped_column(Date, nullable=False)
    hora_retirada: Mapped[Time] = mapped_column(Time, nullable=False)
    hora_prevista_devolucao: Mapped[Time] = mapped_column(Time, nullable=False)
    hora_devolucao: Mapped[Time] = mapped_column(Time, nullable=True)
    status: Mapped[String] = mapped_column(String(9), nullable=False)

    tb_chave = relationship("TB_Chave", back_populates="tb_retirada")

    tb_responsavel = relationship("TB_Responsavel", back_populates="tb_retirada")

    tb_reserva = relationship("TB_Reserva", back_populates="tb_retirada")


class TB_RetiradaSchema(Schema):
    retirada_id = fields.Int(dump_only=True)

    chave_id = fields.Int(
        required=True,
        validate=validate_positive,
        error_messages=montarDicionarioDeMensagemDeErro("chave_id", ["required", "null", "validator_failed"]))

    responsavel_id = fields.Int(
        required=True,
        validate=validate_positive,
        error_messages=montarDicionarioDeMensagemDeErro("responsavel_id", ["required", "null", "validator_failed"]))

    #allow_none=True, após o required
    reserva_id = fields.Int(
        required=False,
        validate=validate_positive,
        error_messages=(montarDicionarioDeMensagemDeErro("responsavel_id", "validator_failed")))

    data_retirada = fields.Date(
        required=True,
        error_messages=montarDicionarioDeMensagemDeErro("data_retirada", ["required", "null", "invalid"]))

    hora_retirada = fields.Time(
        required=True,
        error_messages=montarDicionarioDeMensagemDeErro("hora_retirada", ["required", "null", "invalid"]))
    
    hora_prevista_devolucao = fields.Time(
        required=True,
        error_messages=montarDicionarioDeMensagemDeErro("hora_prevista_devolucao", ["required", "null", "invalid"]))
    
    hora_devolucao = fields.Time(
        required=False,
        error_messages=montarDicionarioDeMensagemDeErro("hora_devolucao", "invalid", "h"))
    
    status = fields.Str(
        required=True,
        validate=validate.OneOf(
            ["retirada", "atrasada", "devolvida"],
            error="O campo status aceita apenas uma dessas opções: retirada, atrasada, devolvida."
        )
    )

@validates_schema
def validate_retirada(self, data, **kwargs):
    validateRetiradaRules(self, data)
