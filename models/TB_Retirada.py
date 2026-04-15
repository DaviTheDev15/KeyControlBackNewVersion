from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Date, Time, String, ForeignKey
from helpers.database import db
from marshmallow import Schema, fields, validate, ValidationError, validates, validates_schema
from flask_restful import fields as flaskFields
from datetime import date, datetime, timedelta

class DateFormat(flaskFields.Raw):
    def format(self, value):
        return value.isoformat() if value else None
    

class TimeFormat(flaskFields.Raw):
    def format(self, value):
        return value.strftime("%H:%M") if value else None
    

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

def validate_positive(value):
    if value is not None and value <= 0:
        raise ValidationError("O valor deve ser um número inteiro não negativo.")
    

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
        error_messages={
                "required": "O campo chave_id é obrigatório.",
                "null":"O campo chave_id não pode ser nulo",
                "validator_failed":"O campo chave_id deve ser valido(Maior que 0) e Corresponder a uma sala existente."        
            })

    responsavel_id = fields.Int(
        required=True,
        validate=validate_positive,
        error_messages={
            "required": "O campo responsavel_id é obrigatório.",
            "null":"O campo responsavel_id não pode ser nulo.",
            "validator_failed":"O campo responsavel_id deve ser valido(Maior que 0) e Corresponder a um responsavel existente."
            })
    

    reserva_id = fields.Int(
        required=False,
        allow_none=True,
        validate=validate_positive,
        error_messages={
            "validator_failed":"O campo responsavel_id deve ser valido(Maior que 0) e Corresponder a um responsavel existente."
        }
    )

    data_retirada = fields.Date(
        required=True,
        error_messages={
            "required": "O campo data_retirada é obrigatório.",
            "null":"O campo data_retirada não pode ser nulo.",
            "invalid": "Formato inválido. Use YYYY-MM-DD."
        }
    )

    hora_retirada = fields.Time(
        required=True,
        error_messages={
            "required": "O campo hora_retirada é obrigatório.",
            "null":"O campo hora_retirada não pode ser nulo.",
            "invalid": "Formato inválido. Use HH:MM."
        })
    
    hora_prevista_devolucao = fields.Time(
        required=True,
        error_messages={
            "required": "O campo hora_prevista_devolucao é obrigatório.",
            "null":"O campo hora_prevista_devolucao não pode ser nulo.",
            "invalid": "Formato inválido. Use HH:MM."
        })
    
    hora_devolucao = fields.Time(
        required=False,
        error_messages={
            "invalid": "Formato inválido. Use HH:MM."
        })
    
    status = fields.Str(
        required=True,
        validate=validate.OneOf(
            ["retirada", "atrasada", "devolvida"],
            error="O campo status aceita apenas uma dessas opções: retirada, atrasada, devolvida."
        )
    )


@validates_schema
def validate_retirada(self, data, **kwargs):
    data_retirada = data.get("data_retirada")
    hora_retirada = data.get("hora_retirada")
    hora_prevista = data.get("hora_prevista_devolucao")
    hora_devolucao = data.get("hora_devolucao")
    status = data.get("status")

    hoje = date.today()
    agora = datetime.now()
    tolerancia = agora - timedelta(minutes=5)

    if not self.partial:
        if data.get("status") != "retirada":
            raise ValidationError({
                "status": "No POST, status deve ser 'retirada'."
            })

    if data_retirada and data_retirada != hoje:
        raise ValidationError({
            "data_retirada": "data_retirada deve ser a data de hoje."
        })

    if data_retirada and data_retirada > hoje:
        raise ValidationError({
            "data_retirada": "data_retirada não pode ser uma data futura."
        })

    if data_retirada == hoje and hora_retirada:
        retirada_dt = datetime.combine(hoje, hora_retirada)

        if retirada_dt < agora - timedelta(minutes=10):
            raise ValidationError({
                "hora_retirada": (
                    "hora_retirada não pode ser muito anterior ao horário atual."
                )
            })

        if retirada_dt < tolerancia:
            raise ValidationError({
                "hora_retirada": (
                    "hora_retirada ultrapassa o limite de tolerância de 5 minutos."
                )
            })

    if hora_retirada and hora_prevista and hora_prevista <= hora_retirada:
        raise ValidationError({
            "hora_prevista_devolucao": (
                "hora_prevista_devolucao deve ser maior que hora_retirada."
            )
        })

    if hora_devolucao and hora_retirada and hora_devolucao < hora_retirada:
        raise ValidationError({
            "hora_devolucao": (
                "hora_devolucao não pode ser anterior a hora_retirada."
            )
        })


    if not self.partial and hora_devolucao:
        raise ValidationError({
            "hora_devolucao": "hora_devolucao não pode ser informada no POST."
        })

    if status == "devolvida" and not hora_devolucao:
        raise ValidationError({
            "hora_devolucao": (
                "hora_devolucao é obrigatória quando status é 'devolvida'."
            )
        })

    if status != "devolvida" and hora_devolucao:
        raise ValidationError({
            "hora_devolucao": (
                "hora_devolucao só deve existir quando status é 'devolvida'."
            )
        })

