from flask_restful import Resource

class IndexResource(Resource):
    def get(self):
        versao = {"versao": "3.0"}
        return versao, 200