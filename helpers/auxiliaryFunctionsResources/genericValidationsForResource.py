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

def responsavelVerification(id):
    from models.TB_Responsavel import TB_Responsavel

    responsavel = db.session.get(TB_Responsavel, id)
    if not responsavel:
        logger.info(f"Responsavel {id} não encontrado")
        abort(404, "Responsavel não encontrado")

def responsavelIsActive(id):
    from models.TB_Responsavel import TB_Responsavel

    responsavel = db.session.get(TB_Responsavel, id)
    if responsavel.ativo == False:
        logger.info(f"Responsavel {id} se encontra Inativo")
        abort(404, "Responsavel Inativo")
        
def reservaVerification(id):
    from models.TB_Reserva import TB_Reserva

    reserva = db.session.get(TB_Reserva, id)
    if not reserva:
        logger.info(f"Reserva {id} não encontrada")
        abort(404, "Reserva não encontrada")

def reservaStatusIsAtiva(id):
    from models.TB_Reserva import TB_Reserva

    reserva = db.session.get(TB_Reserva, id)
    if reserva.status == "ativa":
        logger.info(f"Reserva {id} está ativa, não pode ser apagada")
        abort(404, "Reserva se encontra ativa, não pode ser apagada")