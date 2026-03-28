from flask_restful import Resource
from flask import request
from models.TB_Usuario import TB_Usuario

from flask_jwt_extended import create_access_token

class AuthResource(Resource):

    def post(self):

        email = request.json.get("email")
        senha = request.json.get("senha")

        usuario = TB_Usuario.query.filter_by(email=email).first()

        if not usuario:
            return {"message": "Usuário não encontrado"}, 404

        if not usuario.check_senha(senha):
            return {"message": "Senha incorreta"}, 401
        
        access_token = create_access_token(
            identity=usuario.usuario_id,
            additional_claims={
                "funcao": usuario.funcao
            }
        )

        return {
            "message": "Login realizado com sucesso",
            "access_token": access_token,
            "usuario": usuario.usuario_nome,
            "funcao": usuario.funcao
        }, 200