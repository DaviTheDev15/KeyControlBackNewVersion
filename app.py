from helpers.application import app, api
from helpers.database import db
from helpers.CORS import cors

from resources.IndexResource import IndexResource
from resources.TB_ResponsavelResource import TB_ResponsaveisResource, TB_ResponsavelResource
from resources.TB_SalaResource import TB_SalasResource, TB_SalaResource
from resources.TB_ChaveResource import TB_ChavesResource, TB_ChaveResource
from resources.TB_ReservaResource import TB_ReservasResource, TB_ReservaResource
from resources.TB_RetiradaResource import TB_RetiradasResource, TB_RetiradaResource
from resources.HistoricoResource import HistoricoResource, HistoricoByIdResource



cors.init_app(app)
api.add_resource(IndexResource, '/')
api.add_resource(TB_ResponsaveisResource, '/responsavel')
api.add_resource(TB_ResponsavelResource, '/responsavel/<int:responsavel_id>')
api.add_resource(TB_SalasResource, '/salas')
api.add_resource(TB_SalaResource, '/salas/<int:sala_id>')
api.add_resource(TB_ChavesResource, '/chaves')
api.add_resource(TB_ChaveResource, '/chaves/<int:chave_id>')
api.add_resource(TB_ReservasResource, '/reservas')
api.add_resource(TB_ReservaResource, '/reservas/<int:reserva_id>')
api.add_resource(TB_RetiradasResource, '/retiradas')
api.add_resource(TB_RetiradaResource, '/retiradas/<int:retirada_id>')
api.add_resource(HistoricoResource, '/historico')
api.add_resource(HistoricoByIdResource, '/historico/<int:retirada_id>')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)