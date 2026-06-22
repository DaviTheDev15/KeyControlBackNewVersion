from flask_restful import Resource, marshal_with
from flask import request
from models.TB_Usuario import TB_Usuario, TB_UsuarioSchema, tb_usuario_fields
from helpers.database import db

schema = TB_UsuarioSchema()

class UsuarioResource(Resource):

    @marshal_with(tb_usuario_fields)
    def post(self):

        data = schema.load(request.json)

        primeiro_usuario = TB_Usuario.query.first() is None
        funcao = "admin" if primeiro_usuario else "responsavel"

        usuario = TB_Usuario(
            usuario_nome=data["usuario_nome"],
            email=data["email"],
            funcao=funcao
        )

        usuario.set_senha(data["senha"])

        db.session.add(usuario)
        db.session.commit()

        return usuario, 201