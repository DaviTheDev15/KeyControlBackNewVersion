from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.TB_Usuario import TB_Usuario


class MeResource(Resource):

    @jwt_required()
    def get(self):
        usuario_id = get_jwt_identity()
        claims     = get_jwt()
 
        usuario = TB_Usuario.query.get(int(usuario_id))
 
        if not usuario:
            return {"message": "Usuário não encontrado"}, 404
 
        return {
            "usuario": usuario.usuario_nome,
            "funcao":  usuario.funcao,
        }, 200