from flask_restful import Resource
from flask import request, make_response, jsonify
from models.Responsavel import TB_Responsavel
from flask_jwt_extended import create_access_token, set_access_cookies

class AuthResource(Resource):

    def post(self):
        data = request.get_json(silent=True)
 
        if not data:
            return {"message": "Corpo da requisição inválido"}, 400
 
        email = data.get("email", "").strip().lower()
        senha = data.get("senha", "")
 
        if not email or not senha:
            return {"message": "Email e senha são obrigatórios"}, 400
 
        usuario = TB_Responsavel.query.filter_by(email=email).first()
 
        if not usuario or not usuario.check_senha(senha):
            return {"message": "Credenciais inválidas"}, 401
        
        access_token = create_access_token(
            identity=str(usuario.responsavel_id),
            additional_claims={
                "funcao": usuario.funcao,
                "nome": usuario.responsavel_nome,
            }
        )
        
        response = make_response(
            jsonify({
                "usuario": usuario.responsavel_nome,
                "funcao": usuario.funcao,
            }),
            200
        )
        
        set_access_cookies(response, access_token)
 
        return response