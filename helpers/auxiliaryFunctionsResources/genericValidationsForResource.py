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

def chaveIsDisponivel(id):
    from models.TB_Chave import TB_Chave

    chave = db.session.get(TB_Chave, id)
    if not chave.disponivel:
        logger.info(f"Chave {id} não está disponivel")
        abort(404, "Chave não está disponivel")

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
    if reserva.status != "ativa":
        logger.info(f"Reserva {id} não está ativa")
        abort(404, "Reserva não está ativa")
    

def reservaStatusIsAtivaInDelete(id):
    from models.TB_Reserva import TB_Reserva

    reserva = db.session.get(TB_Reserva, id)
    if reserva.status == "ativa":
        logger.info(f"Reserva {id} está ativa, não pode ser apagada")
        abort(404, "Reserva se encontra ativa, não pode ser apagada")

def retiradaVerification(id):
    from models.TB_Retirada import TB_Retirada

    retirada = db.session.get(TB_Retirada, id)
    if not retirada:
        logger.info(f"Retirada {id} não encontrada")
        abort(404, "Retirada não encontrada")

def retiradaStatus(id):
    from models.TB_Retirada import TB_Retirada

    retirada = db.session.get(TB_Retirada, id)
    if retirada.status == "retirada" or retirada.status == "atrasada":
        logger.info(f"A retirada {id} ainda não foi finalizada, por isso não poderá ser deletada")
        abort(409, "A retirada ainda não foi finalizada, por isso não poderá ser deletada")