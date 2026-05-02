from flask import request, abort
from flask_restful import Resource, marshal
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from helpers.database import db
from helpers.logging import logger, log_exception
from helpers.redis_cache import redis_client
from helpers.solr import solr_client
from helpers.auxiliaryFunctionsResources.solrFunctions import solrVerificationSala, adicionarSala, deletarSala
from helpers.auxiliaryFunctionsResources.redisCacheFunctions import preencherRedisCache, verificarRedisCache
from helpers.auxiliaryFunctionsResources.genericValidationsForResource import salaVerification

from models.TB_Sala import TB_Sala, TB_SalaSchema, tb_sala_fields
from models.TB_Chave import TB_Chave

from werkzeug.exceptions import HTTPException 

import json

class TB_SalasResource(Resource):
    def get(self):
        logger.info("GET ALL - Listagem de Salas")

        page = int(request.args.get("page", 1))

        per_page = int(request.args.get("per_page", 50))

        text = request.args.get("q", "*")

        if text and text != "*":
            return solrVerificationSala(text, page, per_page)

        try:
            cacheKey = f"salas:page={page}:per_page={per_page}"

            cache = verificarRedisCache("Salas", cacheKey)

            if cache:
                logger.info("Retornando Salas do Redis!")
                return json.loads(cache), 200
            
        except Exception:
            logger.info("Erro ao acessar o Redis Cache")
            log_exception("Erro ao acessar o Redis Cache")
            abort(500, description="Erro ao acessar o Redis Cache")

        try:
            logger.info("Redis Cache estava vazio!")
            logger.info("Buscando no Banco de Dados!")

            query = db.select(TB_Sala).order_by(TB_Sala.sala_id)

            salas = db.session.execute(query).scalars().all()

            resposta = marshal(salas, tb_sala_fields)

            preencherRedisCache(cacheKey, resposta)

            logger.info("Retornando Salas do Banco de Dados!")

            return resposta, 200
        
        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao buscar TB_Salas")
            logger.info("Erro SQLAlchemy ao buscar TB_Salas")
            db.session.rollback()
            abort(500, description="Erro ao buscar TB_Salas no banco de dados.")

        except HTTPException:
            raise

        except Exception:
            log_exception("Erro inesperado ao buscar TB_Salas")
            logger.info("Erro inesperado ao buscar TB_Salas")
            abort(500, description="Erro interno inesperado.")


    def post(self):
        logger.info("POST - Nova Sala")        

        schema = TB_SalaSchema()

        dados = request.get_json()

        try:
            validado = schema.load(dados)

            nova_sala = TB_Sala(**validado)

            db.session.add(nova_sala)

            db.session.commit()

            resposta = marshal(nova_sala, tb_sala_fields)

            adicionarSala(nova_sala)
            
            redis_client.delete_pattern("salas:*")

            return resposta, 201

        except ValidationError as err:
            logger.info(f"Dados inválidos, detalhes {err.messages}")
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422

        except SQLAlchemyError:
            logger.info("Erro SQLAlchemy ao inserir Sala")
            log_exception("Erro SQLAlchemy ao inserir Sala")
            db.session.rollback()
            abort(500, "Erro ao inserir Sala.")
            
        except HTTPException:
            raise

        except Exception:
            logger.info("Erro inesperado ao inserir Sala")
            log_exception("Erro inesperado ao inserir Sala")
            abort(500, "Erro interno Sala.")        


class TB_SalaResource(Resource):
    def get(self, sala_id):
        logger.info(f"GET BY ID - Sala {sala_id}")

        try:
            cacheKey = f"salas:{sala_id}"

            cache = verificarRedisCache("Salas", cacheKey)
            if cache:
                logger.info(f"Retornando sala {sala_id} do Redis!")
                return json.loads(cache), 200
        
        except Exception:
            logger.info("Erro ao acessar o Redis Cache")
            log_exception("Erro ao acessar o Redis Cache")
            abort(500, description="Erro ao acessar o Redis Cache")
        
        try:
            logger.info("Redis Cache estava vazio!")
            logger.info("Buscando no Banco de Dados!")

            sala = db.session.get(TB_Sala, sala_id)

            salaVerification(sala_id)
            
            resposta = marshal(sala, tb_sala_fields)

            preencherRedisCache(cacheKey, resposta)

            logger.info(f"Sala {sala_id} retornado do Banco de Dados!")

            return resposta, 200
        
        except SQLAlchemyError:
            logger.info(f"Erro SQLAlchemy ao buscar Sala {sala_id}")
            log_exception("Erro SQLAlchemy ao buscar Sala")
            abort(500, description="Erro ao buscar Sala no banco de dados.")

        except HTTPException:
            raise

        except Exception:
            logger.info("Erro inesperado ao buscar Sala")
            log_exception("Erro inesperado ao buscar Sala")
            abort(500, "Erro interno inesperado.")

    def put(self, sala_id):
        logger.info(f"PUT - Editando Sala {sala_id}")

        schema = TB_SalaSchema()

        dados = request.get_json()

        try:
            sala = db.session.get(TB_Sala, sala_id)

            salaVerification(sala_id)

            nomeAntigo = sala.sala_nome

            atualizados = schema.load(dados, partial=True)

            for campo, valor in atualizados.items():
                setattr(sala, campo, valor)
            
            if "sala_nome" in atualizados and nomeAntigo != sala.sala_nome:
                chaves = db.session.query(TB_Chave)\
                    .filter(TB_Chave.sala_id == sala.sala_id)\
                    .order_by(TB_Chave.chave_id)\
                    .all()

                for i, chave in enumerate(chaves, start=1):
                    chave.chave_nome = f"Chave {sala.sala_nome} {i:02d}"

            db.session.commit()

            adicionarSala(sala)

            redis_client.delete(f"salas:*")

            return marshal(sala, tb_sala_fields), 200
        
        except ValidationError as err:
            logger.info(f"Dados inválidos, detalhes: {err.messages}")
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422

        except SQLAlchemyError:
            logger.info(f"Erro SQLAlchemy ao atualizar Sala {sala_id}")
            log_exception("Erro SQLAlchemy ao atualizar Sala")
            db.session.rollback()
            abort(500, description="Erro ao atualizar Sala.")

        except HTTPException:
            raise

        except Exception:
            logger.info(f"Erro inesperado ao atualizar Sala {sala_id}")
            log_exception("Erro inesperado ao atualizar Sala")
            abort(500, description="Erro interno inesperado.")
        

    def delete(self, sala_id):
        logger.info(f"DELETE - Apagando Sala {sala_id}")
        
        try:
            sala = db.session.get(TB_Sala, sala_id)

            salaVerification(sala_id)
            
            db.session.delete(sala)

            db.session.commit()

            deletarSala(sala_id)

            redis_client.delete(f"salas:*")

            return {"mensagem":"Sala removida com sucesso"}, 200
        
        except SQLAlchemyError:
            logger.info(f"Erro SQLAlchemy ao remover Sala {sala_id}")
            log_exception("Erro SQLAlchemy ao remover Sala")
            db.session.rollback()
            abort(500, description="Erro ao remover Sala.")
        
        except HTTPException:
            raise

        except Exception:
            logger.info("Erro inesperado ao remover Sala")
            log_exception("Erro inesperado ao remover Sala")
            abort(500, "Erro interno inesperado.")
