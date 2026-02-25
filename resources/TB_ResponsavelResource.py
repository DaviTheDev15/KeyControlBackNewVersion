from flask import request, abort
from flask_restful import Resource, marshal
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from helpers.database import db
from helpers.logging import logger, log_exception
from helpers.redis_cache import redis_client
from helpers.solr import solr_client

from models.TB_Responsavel import TB_Responsavel, TB_ResponsavelSchema, tb_responsavel_fields
import json


class TB_ResponsaveisResource(Resource):
    def get(self):
        logger.info("GET ALL - Listagem de Responsáveis")

        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 50))
        text = request.args.get("q", "*")

        if text and text != "*":
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

        try:
            cache_key = f"responsaveis:page={page}:per_page={per_page}"

            logger.info("Verificando se há dados dos responsáveis no Redis!")
            cache = redis_client.get(cache_key)
            if cache:
                logger.info("Retornando responsáveis do Redis!")
                return json.loads(cache), 200
        

        except Exception:
            logger.info("Erro ao acessar o Redis Cache")
            log_exception("Erro ao acessar o Redis Cache")
            abort(500, description="Erro ao acessar o Redis Cache")


        try:
            logger.info("Redis Cache estava vazio!")
            logger.info("Buscando no Banco de Dados!")
            query = db.select(TB_Responsavel).order_by(TB_Responsavel.responsavel_id)
            responsaveis = db.session.execute(
                query.offset((page - 1) * per_page).limit(per_page)
            ).scalars().all()

            resposta = marshal(responsaveis, tb_responsavel_fields)

            redis_client.setex(cache_key, 30, json.dumps(resposta))
            logger.info("Retornando responsáveis do Banco de Dados!")
            return resposta, 200
        
        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao buscar TB_Responsavel")
            logger.info("Erro SQLAlchemy ao buscar TB_Responsavel")
            db.session.rollback()
            abort(500, description="Erro ao buscar TB_Responsavel no banco de dados.")

        except Exception:
            log_exception("Erro inesperado ao buscar TB_Responsavel")
            logger.info("Erro inesperado ao buscar TB_Responsavel")
            abort(500, description="Erro interno inesperado.")

        
    def post(self):
        logger.info("POST - Novo Responsável")
        
        schema = TB_ResponsavelSchema()
        dados = request.get_json()

        try:
            validado = schema.load(dados)
            novo_responsavel = TB_Responsavel(**validado)

            db.session.add(novo_responsavel)
            db.session.commit()

            resposta = marshal(novo_responsavel, tb_responsavel_fields)

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

            redis_client.delete_pattern("responsaveis:*")

            return resposta, 201
        

        except ValidationError as err:
            logger.info(f"Dados inválidos, detalhes {err.messages}")
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422
        

        except SQLAlchemyError:
            logger.info("Erro SQLAlchemy ao inserir Responsavel")
            log_exception("Erro SQLAlchemy ao inserir Responsavel")
            db.session.rollback()
            abort(500, "Erro ao inserir Responsavel.")

        except Exception:
            logger.info("Erro inesperado ao inserir Responsavel")
            log_exception("Erro inesperado ao inserir Responsavel")
            abort(500, "Erro interno inesperado.")


class TB_ResponsavelResource(Resource):
    def get(self, responsavel_id):
        logger.info(f"GET BY ID - Responsável ID {responsavel_id}")

        try:
            cache_key = f"responsavel:{responsavel_id}"

            logger.info(f"Verificando se há dados do Responsavel {responsavel_id} no Redis!")
            cache = redis_client.get(cache_key)
            if cache:
                logger.info(f"Retornando responsável {responsavel_id} do Redis!")
                return json.loads(cache), 200
        
        except Exception:
            logger.info("Erro ao acessar o Redis Cache")
            log_exception("Erro ao acessar o Redis Cache")
            abort(500, description="Erro ao acessar o Redis Cache")
            
        try:
            logger.info("Redis Cache estava vazio!")
            logger.info("Buscando no Banco de Dados!")
            responsavel = db.session.get(TB_Responsavel, responsavel_id)
            if not responsavel:
                logger.info(f"Responsável {responsavel_id} não encontrado")
                return {"erro": "Responsável não encontrado"}, 404

            resposta = marshal(responsavel, tb_responsavel_fields)

            redis_client.setex(cache_key, 30, json.dumps(resposta))
            logger.info(f"Responsável {responsavel_id} retornado do Banco de Dados!")
            return resposta, 200

        except SQLAlchemyError:
            logger.info(f"Erro SQLAlchemy ao buscar Responsável {responsavel_id}")
            log_exception("Erro SQLAlchemy ao buscar Responsável")
            abort(500, description="Erro ao buscar Responsável no banco de dados.")

        except Exception:
            logger.info("Erro inesperado ao buscar Responsavel")
            log_exception("Erro inesperado ao buscar Responsavel")
            abort(500, "Erro interno inesperado.")


    def put(self, responsavel_id):
        logger.info(f"PUT - Editando Responsável {responsavel_id}")

        schema = TB_ResponsavelSchema()
        dados = request.get_json()

        try:
            responsavel = db.session.get(TB_Responsavel, responsavel_id)
            if not responsavel:
                logger.info(f"Responsável {responsavel_id} não encontrado")
                return {"erro": "Responsável não encontrado"}, 404

            atualizados = schema.load(dados, partial=True)

            for campo, valor in atualizados.items():
                setattr(responsavel, campo, valor)

            db.session.commit()

            try:
                doc_solr = {
                    "id": str(responsavel.responsavel_id),
                    "responsavel_id": responsavel.responsavel_id,
                    "responsavel_nome": responsavel.responsavel_nome,
                    "responsavel_cpf": responsavel.responsavel_cpf,
                    "responsavel_siap": responsavel.responsavel_siap,
                    "ativo": responsavel.ativo,
                    "responsavel_data_nascimento": str(responsavel.responsavel_data_nascimento) if responsavel.responsavel_data_nascimento else None
                }
                solr_client.add([doc_solr])
                logger.info(f"Responsável {responsavel_id} atualizado no Solr.")
            except Exception:
                log_exception(f"Falha ao atualizar Solr. Id: {responsavel_id}")

            redis_client.delete(f"responsaveis:*")

            return marshal(responsavel, tb_responsavel_fields), 200

        except ValidationError as err:
            logger.info(f"Dados inválidos, detalhes: {err.messages}")
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422

        except SQLAlchemyError:
            logger.info("Erro SQLAlchemy ao atualizar Responsável")
            log_exception("Erro SQLAlchemy ao atualizar Responsável")
            db.session.rollback()
            abort(500, description="Erro ao atualizar Responsável.")

        except Exception:
            logger.info("Erro inesperado ao atualizar Responsável")
            log_exception("Erro inesperado ao atualizar Responsável")
            abort(500, description="Erro interno inesperado.")


    def delete(self, responsavel_id):
        logger.info("DELETE - Apagando Responsável")

        try:
            responsavel = db.session.get(TB_Responsavel, responsavel_id)
            if not responsavel:
                logger.info(f"Responsável {responsavel_id} não encontrado")
                return {"erro": "Responsável não encontrado"}, 404
            if responsavel.ativo:
                logger.info(f"Responsável {responsavel_id} se encontra ativo na instituição, não se pode apagar responsáveis ativos")
                return {"erro":"Responsável se encontra ativo na instituição, não se pode apagar responsáveis ativos"}, 409

            db.session.delete(responsavel)
            db.session.commit()

            try:
                solr_client.delete(id=str(responsavel_id))
                logger.info(f"Responsável {responsavel_id} removido do Solr.")
            except Exception:
                log_exception(f"Falha ao remover Solr. Id: {responsavel_id}")

            redis_client.delete(f"responsaveis:*")

            return {"mensagem": "Responsável removido com sucesso"}, 200

        except SQLAlchemyError:
            logger.info("Erro SQLAlchemy ao remover Responsável")
            log_exception("Erro SQLAlchemy ao remover Responsável")
            db.session.rollback()
            abort(500, description="Erro ao remover Responsável.")

        except Exception:
            logger.info("Erro inesperado ao remover Responsavel")
            log_exception("Erro inesperado ao remover Responsavel")
            abort(500, "Erro interno inesperado.")