from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.Responsavel import TB_Responsavel


class MeResource(Resource):

    @jwt_required()
    def get(self):
        responsavel_id = get_jwt_identity()
        claims = get_jwt()
 
        responsavel = TB_Responsavel.query.get(int(responsavel_id))
 
        if not responsavel:
            return {"message": "Usuário não encontrado"}, 404
 
        return {
            "id": responsavel.responsavel_id,
            "usuario": responsavel.responsavel_nome,
            "data_nascimento":(
                responsavel.responsavel_data_nascimento.isoformat()
                if responsavel.responsavel_data_nascimento
                else None
                ),
            "email": responsavel.email,
            "funcao":  responsavel.funcao,
        }, 200
