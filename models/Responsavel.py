from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Date, Boolean
from helpers.database import db
from helpers.validation_functions.genericValidations import DateFormat, validate_positive, montarDicionarioDeMensagemDeErro
from helpers.validation_functions.responsavelSchemaValidation import validar_unique_cpf, validar_unique_siap, validar_unique_matricula, validar_unique_email, validarIdade
from marshmallow import Schema, fields, validate, validates
from flask_restful import fields as flaskFields

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

tb_responsavel_fields = {
    'responsavel_id': flaskFields.Integer,
    'responsavel_nome': flaskFields.String,
    'responsavel_siap': flaskFields.String,
    'responsavel_matricula': flaskFields.String,
    'responsavel_cpf': flaskFields.String,
    'responsavel_data_nascimento': DateFormat,
    'email': flaskFields.String,
    'funcao': flaskFields.String,
    'ativo': flaskFields.Boolean
}
    
class TB_Responsavel(db.Model):
    __tablename__ = "tb_responsavel"

    responsavel_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    responsavel_nome: Mapped[str] = mapped_column(String(255), nullable=False)
    responsavel_siap: Mapped[str] = mapped_column(String(7), nullable=True, unique=True)
    responsavel_matricula: Mapped[str] = mapped_column(String(12), nullable=True)
    responsavel_cpf: Mapped[str] = mapped_column(String(14), nullable=False, unique=True)
    responsavel_data_nascimento: Mapped[Date] = mapped_column(Date, nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    senha: Mapped[str] = mapped_column(String(255), nullable=False)
    funcao: Mapped[str] = mapped_column(String(255), nullable=False, default="responsavel")
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False)
    
    tb_reserva = relationship("TB_Reserva", back_populates="tb_responsavel")

    tb_retirada = relationship("TB_Retirada", back_populates="tb_responsavel")

    def set_senha(self, senha_plain: str):
        self.senha = ph.hash(senha_plain)
 
    def check_senha(self, senha_plain: str):
        try:
            return ph.verify(self.senha, senha_plain)
        except VerifyMismatchError:
            return False


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
    
    responsavel_matricula = fields.Str(
        required=False,
        validate=validate.Length(equal=12, error="O campo responsavel_matricula deve ter exatamente 12 caracteres."),
        error_messages=montarDicionarioDeMensagemDeErro("responsavel_matricula", "null")
    )
    
    responsavel_cpf = fields.Str(
        required=True,                         
        validate=validate.Length(equal=14, error="O campo responsavel_cpf deve ter exatamente 14 caracteres."),
        error_messages=montarDicionarioDeMensagemDeErro("responsavel_cpf", ["required","null"]))
    
    responsavel_data_nascimento = fields.Date(
        required=True,
        validate=validarIdade,
        error_messages=montarDicionarioDeMensagemDeErro("responsavel_data_nascimento", ["required", "invalid"], "y"))

    email = fields.Email(
        required=True,
        error_messages=montarDicionarioDeMensagemDeErro("email", ["required", "invalid"]))
 
    senha = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=8, max=255, error="O campo senha deve ter entre 8 a 255 caracteres"),
        error_messages=montarDicionarioDeMensagemDeErro("senha", ["required", "null"]))
 
    funcao = fields.Str(dump_only=True)

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
        
    @validates("responsavel_matricula")
    def validate_unique_matricula(self, value, **kwargs):
        validar_unique_matricula(value)

    @validates("email")
    def validate_unique_email(self, value, **kwargs):
        validar_unique_email(value)
