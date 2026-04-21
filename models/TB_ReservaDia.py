from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer
from helpers.database import db
from marshmallow import Schema, fields, validate
from helpers.validation_functions.genericValidations import validate_positive, montarMensagemDeErro

class TB_ReservaDia(db.Model):
    __tablename__ = "tb_reserva_dia"

    reserva_dia_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reserva_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("tb_reserva.reserva_id", ondelete="CASCADE"), nullable=False)
    dia_semana: Mapped[int] = mapped_column(
        Integer, nullable=False)
    
    tb_reserva = relationship("TB_Reserva", back_populates="tb_reserva_dia")


class TB_ReservaDiaSchema(Schema):
    reserva_dia_id = fields.Int(dump_only=True)

    reserva_id = fields.Int(
        required=True,
        validate=validate_positive,
        error_messages=montarMensagemDeErro("reserva_id", ["required", "null", "validator_failed"]))

    dia_semana = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=7),
        error_messages=montarMensagemDeErro("dia_semana", "required"))