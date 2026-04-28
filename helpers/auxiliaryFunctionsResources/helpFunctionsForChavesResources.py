from helpers.database import db
from sqlalchemy import func

def gerar_nome_da_chave(sala_id):
    from models.TB_Chave import TB_Chave
    from models.TB_Sala import TB_Sala
    sala = db.session.get(TB_Sala, sala_id)
    if not sala:
        return {"erro":"Sala não encontrada"}, 404
    total = db.session.query(func.count(TB_Chave.chave_id)).filter(TB_Chave.sala_id == sala_id).scalar()
    numero = total + 1
   
    return f"Chave {sala.sala_nome} {numero:02d}"