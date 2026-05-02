from flask import request, abort
from flask_restful import Resource, marshal
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from helpers.database import db
from helpers.logging import logger, log_exception
from helpers.redis_cache import redis_client
from helpers.solr import solr_client
from helpers.auxiliaryFunctionsResources.solrFunctions import solrVerificationResponsavel, adicionarResponsavel, deletarResponsavel
from helpers.auxiliaryFunctionsResources.redisCacheFunctions import preencherRedisCache, verificarRedisCache
from helpers.auxiliaryFunctionsResources.genericValidationsForResource import responsavelVerification, responsavelIsActive

from models.TB_Responsavel import TB_Responsavel, TB_ResponsavelSchema, tb_responsavel_fields
from werkzeug.exceptions import HTTPException 
import json

class TB_ResponsaveisResource(Resource):
    def get(self):
        logger.info("GET ALL - Listagem de Responsáveis")

        page = int(request.args.get("page", 1))

        per_page = int(request.args.get("per_page", 50))

        text = request.args.get("q", "*")

        if text and text != "*":
            return solrVerificationResponsavel(text, page, per_page)

        try:
            cacheKey = f"responsaveis:page={page}:per_page={per_page}"

            cache = verificarRedisCache("Responsaveis", cacheKey)

            if cache:
                logger.info("Retornando responsáveis do Redis!")
                return json.loads(cache), 200
        
        except Exception:
            log_exception("Erro ao retornar o Redis Cache")
            abort(500, description="Erro ao retornar o Redis Cache")


        try:
            logger.info("Redis Cache estava vazio!")
            logger.info("Buscando no Banco de Dados!")

            query = db.select(TB_Responsavel).order_by(TB_Responsavel.responsavel_id)

            responsaveis = db.session.execute(
                query.offset((page - 1) * per_page).limit(per_page)
            ).scalars().all()

            resposta = marshal(responsaveis, tb_responsavel_fields)

            preencherRedisCache(cacheKey, resposta)

            logger.info("Retornando responsáveis do Banco de Dados!")

            return resposta, 200
        
        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao buscar TB_Responsavel")
            db.session.rollback()
            abort(500, description="Erro ao buscar TB_Responsavel no banco de dados.")

        except HTTPException:
            raise

        except Exception:
            log_exception("Erro inesperado ao buscar TB_Responsavel")
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

            adicionarResponsavel(novo_responsavel)

            redis_client.delete_pattern("responsaveis:*")

            return resposta, 201

        except ValidationError as err:
            logger.info(f"Dados inválidos, detalhes {err.messages}")
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422

        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao inserir Responsavel")
            db.session.rollback()
            abort(500, "Erro ao inserir Responsavel.")

        except HTTPException:
            raise

        except Exception:
            log_exception("Erro inesperado ao inserir Responsavel")
            abort(500, "Erro interno inesperado.")


class TB_ResponsavelResource(Resource):
    def get(self, responsavel_id):
        logger.info(f"GET BY ID - Responsável ID {responsavel_id}")

        try:
            cacheKey = f"responsaveis:{responsavel_id}"

            cache = verificarRedisCache("Responsavel", cacheKey)
            if cache:
                logger.info(f"Retornando responsável {responsavel_id} do Redis!")
                return json.loads(cache), 200
        
        except Exception:
            log_exception("Erro ao retornar o Redis Cache")
            abort(500, description="Erro ao acessar o Redis Cache")
            
        try:
            logger.info("Redis Cache estava vazio!")
            logger.info("Buscando no Banco de Dados!")

            responsavel = db.session.get(TB_Responsavel, responsavel_id)

            responsavelVerification(responsavel_id)

            resposta = marshal(responsavel, tb_responsavel_fields)

            preencherRedisCache(cacheKey, resposta)

            logger.info(f"Responsável {responsavel_id} retornado do Banco de Dados!")

            return resposta, 200

        except SQLAlchemyError:
            logger.info(f"Erro SQLAlchemy ao buscar Responsável {responsavel_id}")
            log_exception("Erro SQLAlchemy ao buscar Responsável")
            abort(500, description="Erro ao buscar Responsável no banco de dados.")

        except HTTPException:
            raise

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

            responsavelVerification(responsavel_id)

            atualizados = schema.load(dados, partial=True)

            for campo, valor in atualizados.items():
                setattr(responsavel, campo, valor)

            db.session.commit()

            adicionarResponsavel(responsavel)

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

        except HTTPException:
            raise

        except Exception:
            logger.info("Erro inesperado ao atualizar Responsável")
            log_exception("Erro inesperado ao atualizar Responsável")
            abort(500, description="Erro interno inesperado.")


    def delete(self, responsavel_id):
        logger.info("DELETE - Apagando Responsável")

        try:
            responsavel = db.session.get(TB_Responsavel, responsavel_id)

            responsavelVerification(responsavel_id)

            responsavelIsActive(responsavel_id)

            db.session.delete(responsavel)
            
            db.session.commit()

            deletarResponsavel(responsavel_id)

            redis_client.delete(f"responsaveis:*")

            return {"mensagem": "Responsável removido com sucesso"}, 200

        except SQLAlchemyError:
            logger.info("Erro SQLAlchemy ao remover Responsável")
            log_exception("Erro SQLAlchemy ao remover Responsável")
            db.session.rollback()
            abort(500, description="Erro ao remover Responsável.")

        except HTTPException:
            raise

        except Exception:
            logger.info("Erro inesperado ao remover Responsavel")
            log_exception("Erro inesperado ao remover Responsavel")
            abort(500, "Erro interno inesperado.")