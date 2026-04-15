from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey
from helpers.database import db
from marshmallow import Schema, fields, validate, ValidationError

def validate_positive(value):
    if value <= 0:
        raise ValidationError("O valor deve ser um número inteiro não negativo.")

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
        error_messages={
            "required":"O campo reserva_id é obrigatório.",
            "null":"O campo reserva_id não pode ser nulo",
            "validator_failed":"O campo reserva_id deve ser valido (Maior que 0) e Corresponder a uma reserva existente."
            })

    dia_semana = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=7),
        error_messages={
            "required": "dia_semana é obrigatório.",
            "invalid": "dia_semana deve ser um número entre 1 e 7."
        }
    )