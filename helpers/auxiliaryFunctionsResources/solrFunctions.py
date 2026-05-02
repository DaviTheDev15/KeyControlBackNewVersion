from helpers.solr import solr_client
from helpers.logging import logger, log_exception
from flask import abort

def solrVerificationResponsavel(text):
    try:
        logger.info(f"Buscando no Solr pelo termo: {text}")
        
        query_solr = f"responsavel_nome:{text}*"

        results = solr_client.search(query_solr)
        
        return list(results), 200

    except Exception as e:
            logger.info("Erro ao buscar no Solr")
            log_exception("Erro ao buscar no Solr")
            abort(500, "Erro ao Buscar no Solr")

def solrVerificationSala(text):
    try:
        logger.info(f"Buscando no Solr pelo termo: {text}")

        query_solr = f"sala_nome:{text}*"

        results = solr_client.search(query_solr)

        return list(results), 200
    
    except Exception as e:
            logger.info("Erro ao buscar no Solr")
            log_exception("Erro ao buscar no Solr")
            abort(500, "Erro ao Buscar no Solr")

def adicionarResponsavel(novo_responsavel):
    try:
        doc_solr = {
            "id": str(novo_responsavel.responsavel_id),
            "responsavel_id": novo_responsavel.responsavel_id,
            "responsavel_nome": novo_responsavel.responsavel_nome,
            "responsavel_cpf": novo_responsavel.responsavel_cpf,
            "responsavel_siap": novo_responsavel.responsavel_siap,
            "ativo": novo_responsavel.ativo,
            "responsavel_data_nascimento": str(novo_responsavel.responsavel_data_nascimento) if novo_responsavel.responsavel_data_nascimento else None
        }
        solr_client.add([doc_solr])
        logger.info(f"Responsável {novo_responsavel.responsavel_id} indexado no Solr.")
    except Exception:
        log_exception(f"Falha ao indexar no Solr. Id: {novo_responsavel.responsavel_id}") 

def adicionarSala(nova_sala):
    try:
        doc_solr = {
            "id": f"sala_{nova_sala.sala_id}",
            "sala_id": nova_sala.sala_id,
            "sala_nome": nova_sala.sala_nome,
            "disponivel": nova_sala.disponivel
        }
        solr_client.add([doc_solr])
        logger.info(f"Sala {nova_sala.sala_id} indexado no Solr.")
    except Exception:
        log_exception(f"Falha ao indexar no Solr. Id: {nova_sala.sala_id}")

def deletarResponsavel(responsavel_id):
    try:
        solr_client.delete(id=str(responsavel_id))
        logger.info(f"Responsável {responsavel_id} removido do Solr.")
    except Exception:
        log_exception(f"Falha ao remover Solr. Id: {responsavel_id}")

def deletarSala(sala_id):
    try:
        solr_client.delete(id=str(sala_id))
        logger.info(f"Sala {sala_id} removido do Solr.")
    except Exception:
        log_exception(f"Falha ao remover Solr. Id: {sala_id}")