from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Date, Boolean
from helpers.database import db
from helpers.validation_functions.genericValidations import DateFormat, validate_positive, montarDicionarioDeMensagemDeErro
from helpers.validation_functions.responsavelSchemaValidation import validar_unique_cpf, validar_unique_siap, validarIdade
from marshmallow import Schema, fields, validate, validates
from flask_restful import fields as flaskFields

tb_responsavel_fields = {
    'responsavel_id': flaskFields.Integer,
    'responsavel_nome': flaskFields.String,
    'responsavel_siap': flaskFields.String,
    'responsavel_cpf': flaskFields.String,
    'responsavel_data_nascimento': DateFormat,
    'ativo': flaskFields.Boolean
}
    
class TB_Responsavel(db.Model):
    __tablename__ = "tb_responsavel"

    responsavel_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    responsavel_nome: Mapped[str] = mapped_column(String(255), nullable=False)
    responsavel_siap: Mapped[str] = mapped_column(String(7), nullable=True, unique=True)
    responsavel_cpf: Mapped[str] = mapped_column(String(14), nullable=False, unique=True)
    responsavel_data_nascimento: Mapped[Date] = mapped_column(Date, nullable=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False)
    
    tb_reserva = relationship("TB_Reserva", back_populates="tb_responsavel")

    tb_retirada = relationship("TB_Retirada", back_populates="tb_responsavel")

class TB_ResponsavelSchema(Schema):
    responsavel_id = fields.Int(dump_only=True) 

    responsavel_nome = fields.Str(
        required=True,
        validate=validate.Length(min=4, max=255, error="O campo responsavel_nome deve ter entre 4 a 255 caracteres."),
        error_messages=montarDicionarioDeMensagemDeErro("responsavel_nome", ["required", "null"]))

    responsavel_siap = fields.Str(
        required=False,  
        validate=validate.Length(equal=7, error="O campo responsavel_siap deve ter exatemente 7 caracteres."),
        error_messages=montarDicionarioDeMensagemDeErro("responsavel_siap", "null"))
    
    responsavel_cpf = fields.Str(
        required=True,                         
        validate=validate.Length(min=11, max=14, error="O campo responsavel_cpf deve ter entre 11 a 14 caracteres."),
        error_messages=montarDicionarioDeMensagemDeErro("responsavel_cpf", ["required","null"]))
    
    responsavel_data_nascimento = fields.Date(
        required=True,
        validate=validarIdade,
        error_messages=montarDicionarioDeMensagemDeErro("responsavel_data_nascimento", ["required", "invalid"], "y"))

    ativo = fields.Boolean(
        required=True,
        error_messages=montarDicionarioDeMensagemDeErro("ativo", ["required", "invalid"], "b")
    )

    @validates("responsavel_cpf")
    def validate_unique_cpf(self, value, **kwargs):
        validar_unique_cpf(value)

    @validates("responsavel_siap")
    def validate_unique_siap(self, value, **kwargs):
        validar_unique_siap(value)