from helpers.database import db

class VW_HistoricoRetiradas(db.Model):
    __tablename__ = "vw_historico_retiradas"
    __table_args__ = {"info": {"is_view": True}}

    retirada_id = db.Column(db.Integer, primary_key=True)

    data_retirada = db.Column(db.Date)
    hora_retirada = db.Column(db.Time)
    hora_prevista_devolucao = db.Column(db.Time)
    hora_devolucao = db.Column(db.Time)

    status = db.Column(db.String)

    sala_id = db.Column(db.Integer)
    sala_nome = db.Column(db.String)

    chave_id = db.Column(db.Integer)
    chave_nome = db.Column(db.String)

    responsavel_id = db.Column(db.Integer)
    responsavel_nome = db.Column(db.String)
