from flask_restful import Resource

class IndexResource(Resource):
    def get(self):
        versao = {"risosrisosrisos": "1.3"}
        return versao, 200