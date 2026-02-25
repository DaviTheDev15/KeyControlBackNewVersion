from flask_restful import Resource

class IndexResource(Resource):
    def get(self):
        versao = {"versão": "2.2"}
        return versao, 200