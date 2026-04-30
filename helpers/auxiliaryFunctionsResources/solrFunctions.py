from helpers.solr import solr_client
from helpers.logging import logger, log_exception
from flask import abort

def solrVerification(text, page, per_page):
        try:
            logger.info(f"Buscando no Solr pelo termo: {text}")
            start = (page - 1) * per_page
            
            query_solr = (
                f"responsavel_nome:{text}~2 OR "
                f"responsavel_cpf:*{text}* OR "
                f"responsavel_siap:*{text}*"
            )

            results = solr_client.search(query_solr, **{
                'start': start,
                'rows': per_page
            })
            
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

def deletarResponsavel(responsavel_id):
    try:
        solr_client.delete(id=str(responsavel_id))
        logger.info(f"Responsável {responsavel_id} removido do Solr.")
    except Exception:
        log_exception(f"Falha ao remover Solr. Id: {responsavel_id}")