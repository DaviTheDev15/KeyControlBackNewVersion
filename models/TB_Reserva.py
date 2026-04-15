from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Date, Time, String, ForeignKey
from helpers.database import db
from marshmallow import Schema, fields, validate, ValidationError, validates, validates_schema
from flask_restful import fields as flaskFields
from datetime import date, datetime


class DateFormat(flaskFields.Raw):
    def format(self, value):
        return value.isoformat() if value else None


class TimeFormat(flaskFields.Raw):
    def format(self, value):
        return value.strftime("%H:%M") if value else None
    

class DiasReservaField(flaskFields.Raw):
    def format(self, value):
        return [d.dia_semana for d in value]    

tb_reserva_fields = {
    'reserva_id': flaskFields.Integer,
    'sala_id': flaskFields.Integer,
    'responsavel_id': flaskFields.Integer,
    'hora_inicio': TimeFormat,
    'hora_fim': TimeFormat,
    'data_inicio': DateFormat,
    'data_fim': DateFormat,
    'frequencia': flaskFields.String, #única semanal quinzenal mensal
    'status': flaskFields.String, #ativa cancelada finalizada
    'dias_semana': DiasReservaField(attribute="tb_reserva_dia") #[1...7] 1 = segunda
}

def validate_positive(value):
    if value <= 0:
        raise ValidationError("O valor deve ser um número inteiro não negativo.")
    

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
        error_messages={
            "required": "O campo sala_id é obrigatório.",
            "null":"O campo sala_id não pode ser nulo",
            "validator_failed":"O campo sala_id deve ser valido(Maior que 0) e Corresponder a uma sala existente."            
        })

    responsavel_id = fields.Int(
        required=True,
        validate=validate_positive,
        error_messages={
            "required": "O campo responsavel_id é obrigatório.",
            "null":"O campo responsavel_id não pode ser nulo.",
            "validator_failed":"O campo responsavel_id deve ser valido(Maior que 0) e Corresponder a um responsavel existente."
            })

    hora_inicio = fields.Time(
        required=True,
        error_messages={
            "required": "O campo hora_inicio é obrigatório.",
            "null":"O campo hora_inicio não pode ser nulo.",
            "invalid": "Formato inválido. Use HH:MM."
        })

    hora_fim = fields.Time(
        required=True,
        error_messages={
            "required": "O campo hora_fim é obrigatório.",
            "null":"O campo hora_fim não pode ser nulo.",
            "invalid": "Formato inválido. Use HH:MM."
        })

    data_inicio = fields.Date(
        required=True,
        error_messages={
            "required": "O campo data_inicio é obrigatório.",
            "null":"O campo data_inicio não pode ser nulo.",
            "invalid": "Formato inválido. Use YYYY-MM-DD."
        }
    )

    data_fim = fields.Date(
        required=True,
        error_messages={
            "required": "O campo data_fim é obrigatório.",
            "null":"O campo data_fim não pode ser nulo.",
            "invalid": "Formato inválido. Use YYYY-MM-DD."
        }
    )

    frequencia = fields.Str(
        required=True,
        validate=validate.OneOf(
            ["única","semanal", "quinzenal", "mensal"],
            error="O campo frequencia aceita apenas uma dessas opções: única, semanal, quinzenal e mensal."
        ),
        error_messages={
            "required":"O campo frequencia é obrigatório",
            "null":"O campo frequencia não pode ser nulo.",
            "validator_failed":"O campo frequencia aceita apenas uma dessas opções: única, semanal, quinzenal e mensal."
        }
    )

    status = fields.Str(
        required=True,
        validate=validate.OneOf(
            ["ativa", "cancelada", "finalizada"],
            error="O campo status aceita apenas uma dessas opções: ativa, cancelada, finalizada."
        )
    )

    dias_semana = fields.List(
        fields.Int(
            validate=validate.Range(min=1, max=7),
            error_messages={
                "invalid": "Dia da semana inválido.",
                "required": "dias_semana deve conter valores entre 1 e 7."
            }
        ),
        required=False,
        load_only=True
    )

    @validates_schema
    def validate_datas_horas(self, data, **kwargs):
        data_inicio = data.get("data_inicio")
        data_fim = data.get("data_fim")
        hora_inicio = data.get("hora_inicio")
        hora_fim = data.get("hora_fim")
        frequencia = data.get("frequencia")
        dias_semana = data.get("dias_semana", [])

        hoje = date.today()
        agora = datetime.now().time()

        if frequencia == "única":
            if data_fim and data_inicio and data_fim != data_inicio:
                raise ValidationError({
                    "data_fim": "Em um reserva única data_fim não pode ser diferente de data_inicio."
                })
        
        if data_inicio and data_inicio < hoje:
            raise ValidationError({
                "data_inicio": "data_inicio não pode ser uma data passada."
            })

        if data_inicio and hora_inicio and data_inicio == hoje and hora_inicio <= agora:
            raise ValidationError({
                "hora_inicio": "hora_inicio não pode ser um horário passado."
            })

        if hora_inicio and hora_fim and hora_fim <= hora_inicio:
            raise ValidationError({
                "hora_fim": "hora_fim deve ser maior que hora_inicio."
            })

        if data_inicio and data_fim and data_fim < data_inicio:
            raise ValidationError({
                "data_fim": "data_fim deve ser maior ou igual a data_inicio."
            })


        if frequencia not in ("única", "mensal"):
            if not dias_semana:
                raise ValidationError({
                    "dias_semana": (
                        "Esta frequência exige a informação de dias_semana."
                    )
                })

            if data_inicio:
                dia_real = data_inicio.weekday() + 1  # 1=segunda ... 7=domingo

                if dia_real not in dias_semana:
                    raise ValidationError({
                        "dias_semana": (
                            f"data_inicio ({data_inicio}) corresponde ao dia "
                            f"{dia_real}, que não está em dias_semana."
                        )
                    })
