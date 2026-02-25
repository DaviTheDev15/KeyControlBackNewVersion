from flask import request, abort
from flask_restful import Resource, marshal
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from helpers.database import db
from helpers.logging import logger, log_exception
from helpers.redis_cache import redis_client

from models.TB_Chave import TB_Chave, TB_ChaveSchema, tb_chave_fields
from models.TB_Sala import TB_Sala
import json

class TB_ChavesResource(Resource):
    def get(self):
        logger.info("GET ALL - Listagem de Chaves")

        try:
            cache_key = "chaves:all"
            cache = redis_client.get(cache_key)

            logger.info("Verificando se há dados das Chaves no Redis!")
            if cache:
                logger.info("Retornando Chaves do Redis!")
                return json.loads(cache), 200
            
        except Exception:
            logger.info("Erro ao acessar o Redis Cache")
            log_exception("Erro ao acessar o Redis Cache")
            abort(500, description="Erro ao acessar o Redis Cache")

        try:
            logger.info("Redis Cache estava vazio!")
            logger.info("Buscando no Banco de Dados!")
            query = db.select(TB_Chave).order_by(TB_Chave.chave_id)
            chaves = db.session.execute(query).scalars().all()

            resposta = marshal(chaves, tb_chave_fields)

            redis_client.setex(cache_key, 30, json.dumps(resposta))
            logger.info("Retornando Chaves do Banco de Dados")
            return resposta, 200
        
        except SQLAlchemyError:
            log_exception("Errp SQLAlchemy ao buscar TB_Chaves")
            logger.info("Erro SQLAlchemy ao buscar TB_Chaves")
            db.session.rollback()
            abort(500, description="Erro ao buscar TB_Chaves no banco de dados")

        except Exception:
            log_exception("Erro inesperado ao buscar TB_Chaves")
            logger.info("Erro inesperado ao buscar TB_Chaves")
            abort(500, description="Erro interno inesperado.")


    def post(self):
        logger.info("POST - Nova Chave")

        schema = TB_ChaveSchema()
        dados = request.get_json()
        try:
            validado = schema.load(dados)
            sala = db.session.get(TB_Sala, validado["sala_id"])
            if not sala:
                logger.info(f"Sala não encontrada, não será possivel cadastrar uma chave para ela")
                return {"erro":"Sala não encontrada"}, 404
            
            nova_chave = TB_Chave(**validado)
            db.session.add(nova_chave)
            db.session.commit()

            resposta = marshal(nova_chave, tb_chave_fields)

            redis_client.delete_pattern("chaves:*")

            return resposta, 201
        
        except ValidationError as err:
            logger.info(f"Dados inválidos, detalhes {err.messages}")
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422
        
        except SQLAlchemyError:
            logger.info("Erro SQLAlchemy ao inserir Chave")
            log_exception("Erro SQLAlchemy ao inserir Chave")
            db.session.rollback()
            abort(500, "Erro ao inserir Chave.")

        except Exception:
            logger.info("Erro inesperado ao inserir Chave")
            log_exception("Erro inesperado ao inserir Chave")
            abort(500, "Erro interno Chave.")


class TB_ChaveResource(Resource):
    def get(self, chave_id):
        logger.info(f"GET BY ID - Chave {chave_id}")

        try:
            cache_key = f"chave:{chave_id}"
            logger.info(f"Verificando se há dados da chave {chave_id} no Redis")
            cache = redis_client.get(cache_key)
            if cache:
                logger.info(f"Retornando chave {chave_id} do Redis!")
                return json.loads(cache), 200
            
        except Exception:
            logger.info("Erro ao acessar o Redis Cache")
            log_exception("Erro ao acessar o Redis Cache")
            abort(500, description="Erro ao acessar o Redis Cache")

        try:
            logger.info("Redis Cache estava vazio!")
            logger.info("Buscando no Banco de Dados!")
            chave = db.session.get(TB_Chave, chave_id)
            if not chave:
                logger.info(f"Chave {chave_id} não encontrada")
                return {"erro": "Chave não encontrada"}, 404
            
            resposta = marshal(chave, tb_chave_fields)

            redis_client.setex(cache_key, 30, json.dumps(resposta))
            logger.info(f"Chave {chave_id} retornado do Banco de Dados!")
            return resposta, 200
        
        except SQLAlchemyError:
            logger.info(f"Erro SQLAlchemy ao buscar Chave {chave_id}")
            log_exception("Erro SQLAlchemy ao buscar Chave")
            abort(500, description="Erro ao buscar Chave no banco de dados")

        except Exception:
            logger.info("Erro inesperado ao buscar Chave")
            log_exception("Erro inesperado ao buscar Chave")
            abort(500, "Erro interno inesperado")

    def put(self, chave_id):
        logger.info(f"PUT - Editando Chave {chave_id}")

        schema = TB_ChaveSchema()
        dados = request.get_json()

        try:
            chave = db.session.get(TB_Chave, chave_id)
            if not chave:
                logger.info(f"Chave não encontrada")
                return {"erro":"Chave não encontrada"}, 404
                            
            atualizados = schema.load(dados, partial=True)

            if "sala_id" in atualizados:
                sala = db.session.get(TB_Sala, atualizados["sala_id"])
                if not sala:
                    logger.info(f"Sala {sala.sala_id}não encontrada, não será possível atualizar chave para essa sala")
                    return {"erro":"Sala não encontrada"} 
            
            for campo, valor in atualizados.items():
                setattr(chave, campo, valor)

            db.session.commit()

            redis_client.delete(f"chave:*")

            return marshal(chave, tb_chave_fields), 200
        
        except ValidationError as err:
            logger.info(f"Dados inválidos, detalhes: {err.messages}")
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422
        
        except SQLAlchemyError:
            logger.info(f"Erro SQLAlchemy ao atualizar Chave {chave_id}")
            log_exception("Erro SQLAlchemy ao atualizar Chave")
            db.session.rollback()
            abort(500, description="Erro ao atualizar Chave.") 

        except Exception:
            logger.info(f"Erro inesperado ao atualizar Chave {chave_id}")
            log_exception("Erro inesperado ao atualizar Chave")
            abort(500, description="Erro interno inesperado.")  

    def delete(self, chave_id):
        logger.info(f"DELETE - Apagando Chave {chave_id}")

        try:
            chave = db.session.get(TB_Chave, chave_id)
            if not chave:
                logger.info(f"Chave {chave_id} não encontrada")
                return {"erro":"Chave não encontrada"}, 404
            if not chave.disponivel:
                logger.info(f"Chave {chave_id} ainda não foi devolvida, por isso não pode ser apagada")
                return {"erro":"Chave está em uso, não pode ser removida"}, 400
            
            db.session.delete(chave)
            db.session.commit()

            redis_client.delete(f"chaves:*")

            return {"mensagem":"Chave removida com sucesso"}, 200

        except SQLAlchemyError:
            logger.info(f"Erro SQLAlchemy ao remover Chave {chave_id}")
            log_exception("Erro SQLAlchemy ao remover Chave")
            db.session.rollback()
            abort(500, description="Erro ao remover Chave.")

        except Exception:
            logger.info("Erro inesperado ao remover Chave")
            log_exception("Erro inesperado ao remover Chave")
            abort(500, "Erro interno inesperado.")                    


            
        