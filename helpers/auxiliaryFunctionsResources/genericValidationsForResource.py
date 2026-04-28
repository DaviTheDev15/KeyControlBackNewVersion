from helpers.database import db
from helpers.logging import logger, log_exception
from flask import abort

def salaVerification(id):
    from models.TB_Sala import TB_Sala

    sala = db.session.get(TB_Sala, id)
    if not sala:
        logger.info(f"Sala {id} não encontrada")
        abort(404, "Sala não encontrada")
    
def chaveVerification(id):
    from models.TB_Chave import TB_Chave

    chave = db.session.get(TB_Chave, id)
    if not chave:
        logger.info(f"Chave {id} não encontrada")
        abort(404, "Chave não encontrada")