from flask_restful import Resource
from flask_jwt_extended import unset_jwt_cookies
from flask import make_response, jsonify


class LogoutResource(Resource):

    def post(self):
        response = make_response(
            jsonify({"message": "Logout realizado com sucesso"}),
            200
        )

        unset_jwt_cookies(response)
        return response