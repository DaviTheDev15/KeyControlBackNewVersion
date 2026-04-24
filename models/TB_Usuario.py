from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from helpers.database import db
from helpers.validation_functions.genericValidations import montarDicionarioDeMensagemDeErro
from marshmallow import Schema, fields, validate, ValidationError, validates
from flask_restful import fields as flaskFields

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

tb_usuario_fields = {
    'usuario_id': flaskFields.Integer,
    'usuario_nome': flaskFields.String,
    'email': flaskFields.String,
    'funcao': flaskFields.String
}

class TB_Usuario(db.Model):
    __tablename__ = "tb_usuario"

    usuario_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    senha: Mapped[str] = mapped_column(String(255), nullable=False)
    funcao: Mapped[str] = mapped_column(String(255), nullable=False)
    
    def set_senha(self, senha_plain: str):
        self.senha = ph.hash(senha_plain)

    def check_senha(self, senha_plain: str):
        try:
            return ph.verify(self.senha, senha_plain)
        except VerifyMismatchError:
            return False

class TB_UsuarioSchema(Schema):
    usuario_id = fields.Int(dump_only=True)
    usuario_nome = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=255, error="O campo usuario_nome deve ter entre 2 a 255 caracteres."),
        error_messages=montarDicionarioDeMensagemDeErro("usuario_nome", ["required", "null"]))
    email = fields.Email(
        required=True,
        error_messages=montarDicionarioDeMensagemDeErro("email", ["required", "invalid"]))
    senha = fields.Str(
        required=True,
        validate=validate.Length(min=8, max=255, error="O campo senha deve ter entre 8 a 255 caracteres"),
        error_messages=montarDicionarioDeMensagemDeErro("senha", ["required", "null"]))
    funcao = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=255, error="O campo funcao deve ter entre 2 a 255 caracteres."),
        error_messages=montarDicionarioDeMensagemDeErro("funcao", ["required", "null"]))

