from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Date, Time, String, ForeignKey
from helpers.database import db
from helpers.validation_functions.genericValidations import TimeFormat, DateFormat, DiasReservaField, validate_positive, montarMensagemDeErro, validateReservaRules
from marshmallow import Schema, fields, validate, validates_schema
from flask_restful import fields as flaskFields

tb_reserva_fields = {
    'reserva_id': flaskFields.Integer,
    'sala_id': flaskFields.Integer,
    'responsavel_id': flaskFields.Integer,
    'hora_inicio': TimeFormat,
    'hora_fim': TimeFormat,
    'data_inicio': DateFormat,
    'data_fim': DateFormat,
    'frequencia': flaskFields.String,
    'status': flaskFields.String,
    'dias_semana': DiasReservaField(attribute="tb_reserva_dia")
}

class TB_Reserva(db.Model):
    __tablename__ = "tb_reserva"

    reserva_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sala_id: Mapped[int] = mapped_column(Integer, ForeignKey("tb_sala.sala_id"), nullable=False)
    responsavel_id: Mapped[int] = mapped_column(Integer, ForeignKey("tb_responsavel.responsavel_id"), nullable=False)
    hora_inicio: Mapped[Time] = mapped_column(Time, nullable=False)
    hora_fim: Mapped[Time] = mapped_column(Time, nullable=False)
    data_inicio: Mapped[Date] = mapped_column(Date, nullable=False)
    data_fim: Mapped[Date] = mapped_column(Date, nullable=False)
    frequencia: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="ativa")

    tb_sala = relationship("TB_Sala", back_populates="tb_reserva")

    tb_responsavel = relationship("TB_Responsavel", back_populates="tb_reserva")

    tb_reserva_dia = relationship("TB_ReservaDia", cascade="all,delete-orphan", back_populates="tb_reserva")

    tb_retirada = relationship("TB_Retirada", back_populates="tb_reserva")


class TB_ReservaSchema(Schema):
    reserva_id = fields.Int(dump_only=True)

    sala_id = fields.Int(
        required=True,
        validate=validate_positive,
        error_messages=montarMensagemDeErro("sala_id", ["required", "null", "validator_failed"]))

    responsavel_id = fields.Int(
        required=True,
        validate=validate_positive,
        error_messages=montarMensagemDeErro("responsavel_id", ["required", "null", "validator_failed"]))

    hora_inicio = fields.Time(
        required=True,
        error_messages=montarMensagemDeErro("hora_inicio", ["required", "null", "invalid"], "h"))

    hora_fim = fields.Time(
        required=True,
        error_messages=montarMensagemDeErro("hora_fim", ["required", "null", "invalid"], "h"))

    data_inicio = fields.Date(
        required=True,
        error_messages=montarMensagemDeErro("data_inicio", ["required", "null", "invalid"], "d"))

    data_fim = fields.Date(
        required=True,
        error_messages=montarMensagemDeErro("data_fim", ["required", "null", "invalid"], "d")
    )

    frequencia = fields.Str(
        required=True,
        validate=validate.OneOf(
            ["única","semanal", "quinzenal", "mensal"],
            error="O campo frequencia aceita apenas uma dessas opções: única, semanal, quinzenal e mensal."
        ),
        error_messages=montarMensagemDeErro("frequencia", ["required", "null"]))

    status = fields.Str(
        required=True,
        validate=validate.OneOf(
            ["ativa", "cancelada", "finalizada"],
            error="O campo status aceita apenas uma dessas opções: ativa, cancelada, finalizada."
        ),
        error_messages=montarMensagemDeErro("status", ["required", "null"])
    )

    dias_semana = fields.List(
        fields.Int(
            validate=validate.Range(min=1, max=7,
            error="O campo dias_semana aceita apenas valores númericos inteiros entre 1 e 7. Sendo 1 = Segunda e 7 = Domingo."),
        ),
        required=False,
        load_only=True
    )

    @validates_schema
    def validateCampos(self, data, **kwargs):
        validateReservaRules(data)