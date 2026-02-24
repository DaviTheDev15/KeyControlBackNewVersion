from flask import request, abort
from flask_restful import Resource, marshal
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text, and_
from helpers.database import db
from helpers.logging import logger, log_exception
from helpers.redis_cache import redis_client

from models.TB_Retirada import TB_Retirada, TB_RetiradaSchema, tb_retirada_fields
from models.TB_Chave import TB_Chave
from models.TB_Responsavel import TB_Responsavel
from models.TB_Reserva import TB_Reserva
from models.TB_Sala import TB_Sala

import json
from datetime import date, datetime, timedelta


class TB_RetiradasResource(Resource):
    def get(self):
        logger.info("GET ALL - Listagem de Retiradas")

        try:
            cache_key = "retiradas:all"
            cache = redis_client.get(cache_key)

            logger.info("Verificando se há dados das Retiradas no Redis!")
            if cache:
                logger.info("Retornando Retiradas do Redis")
                return json.loads(cache), 200
            
        except Exception:
            logger.info("Erro ao acessar o Redis Cache")
            log_exception("Erro ao acessar Redis")
            abort(500, "Erro ao acessar cache")

        try:
            logger.info("Redis Cache estava vazio!")
            logger.info("Buscando no Banco de Dados!")

            query = db.select(TB_Retirada).order_by(TB_Retirada.retirada_id)

            retiradas = db.session.execute(query).scalars().all()

            resposta = marshal(retiradas, tb_retirada_fields)

            redis_client.setex(cache_key, 30, json.dumps(resposta))

            logger.info("Retornando Retiradas do Banco de Dados")
            return resposta, 200
        
        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao buscar TB_Retiradas")
            logger.info("Erro SQLAlchemy ao buscar TB_Retirads")
            db.session.rollback()
            abort(500, "Erro ao buscar TB_Retiradas no banco de dados")

        except Exception:
            log_exception("Erro inesperado ao buscar TB_Retiradas")
            logger.info("Erro inesperado ao buscar TB_Retiradas")
            abort(500, description="Erro interno inesperado.")

    def post(self):
        logger.info("Post - Nova Retirada")
        dados = request.get_json()
        schema = TB_RetiradaSchema()

        try:
            validado = schema.load(dados)
            hoje = date.today()
            agora = datetime.now().time()

            if validado.get("data_retirada") != hoje:
                logger.info("Não é possivel fazer retirada para um dia diferente de hoje")
                return {"erro": "Data inválida"}, 404


            if validado.get("reserva_id") in (0, "0"):
                validado["reserva_id"] = None


            reserva = None

            if validado.get("reserva_id") is not None:
                reserva = db.session.get(TB_Reserva, validado["reserva_id"])
                if not reserva:
                    logger.info("Reserva não encontrada")
                    return {"erro": "Reserva não encontrada"}, 404

                if reserva.status != "ativa":
                    logger.info("Reserva não está ativa")
                    return {"erro": "Reserva não está ativa"}, 409


                if not (reserva.data_inicio <= hoje <= reserva.data_fim):
                    logger.info("Hoje não está dentro do período da reserva")
                    return {"erro": "Hoje não está dentro do período da reserva"}, 409

                if reserva.frequencia not in ("única", "mensal"):
                    dia_semana_hoje = hoje.isoweekday()
                    dias_permitidos = [d.dia_semana for d in reserva.tb_reserva_dia]

                    if dia_semana_hoje not in dias_permitidos:
                        logger.info("Hoje não é um dia permitido pela reserva")
                        return {"erro": "Hoje não é um dia permitido pela reserva"}, 409
                    
                    hora_retirada = validado["hora_retirada"]

                    hora_minima = (
                        datetime.combine(hoje, reserva.hora_inicio) - timedelta(minutes=10)
                    ).time()

                    if not (hora_minima <= hora_retirada <= reserva.hora_fim):
                        return {
                            "erro": "Retirada fora do intervalo permitido da reserva"
                        }, 409
                

            chave = db.session.get(TB_Chave, validado["chave_id"])
            if not chave:
                logger.info("Chave não encontrada")
                return {"erro": "Chave não encontrada"}, 404

            sala = db.session.get(TB_Sala, chave.sala_id)

            if reserva and reserva.sala_id != chave.sala_id:
                return {
                    "erro": "Reserva não pertence à sala da chave informada"
                }, 409

            if not chave.disponivel:
                logger.info("Chave ou sala indisponível")
                return {
                    "erro": "Chave e a Sala à qual ela pertence não estão disponíveis no momento"
                }, 409

            retirada_ativa = (
                db.session.query(TB_Retirada)
                .join(TB_Chave, TB_Retirada.chave_id == TB_Chave.chave_id)
                .filter(
                    TB_Chave.sala_id == chave.sala_id,
                    TB_Retirada.status.in_(["retirada", "atrasada"])
                )
                .first()
            )

            if retirada_ativa:
                logger.info("Já existe uma retirada ativa para esta sala")
                return {"erro": "Já existe uma retirada ativa para esta sala"}, 409

            responsavel = db.session.get(TB_Responsavel, validado["responsavel_id"])
            if not responsavel or not responsavel.ativo:
                logger.info("Responsável inválido ou inativo")
                return {"erro": "Responsável inválido ou inativo"}, 400

            retirada = TB_Retirada(**validado)
            db.session.add(retirada)

            chave.disponivel = False
            sala.disponivel = False

            db.session.commit()

            redis_client.delete_pattern("retiradas:*")

            return marshal(retirada, tb_retirada_fields), 201

        except ValidationError as err:
            logger.info(f"Dados inválidos: {err.messages}")
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422

        except SQLAlchemyError:
            logger.info("Erro SQLAlchemy ao inserir Retirada")
            log_exception("Erro SQLAlchemy ao criar Retirada")
            db.session.rollback()
            abort(500, "Erro ao criar Retirada")

        except Exception:
            logger.info("Erro inesperado ao inserir Retirada")
            log_exception("Erro inesperado ao inserir Retirada")
            abort(500, "Erro interno Retirada.")


class TB_RetiradaResource(Resource):
    def get(self, retirada_id):
        logger.info(f"GET - Retirada {retirada_id}")

        try:
            cache_key = f"retirada:{retirada_id}"
            logger.info(f"Verificando se há dados da retirada {retirada_id} no Redis")
            cache = redis_client.get(cache_key)
            if cache:
                logger.info(f"Retornando retirada {retirada_id} do Redis!")
                return json.loads(cache), 200
            
        except Exception:
            logger.info("Erro ao acessar o Redis Cache")
            log_exception("Erro ao acessar Redis")
            abort(500, description="Erro ao acessar o Redis Cache")


        try:
            logger.info("Redis Cache estava vazio!")
            logger.info("Buscando no Banco de Dados!")
            retirada = db.session.get(TB_Retirada, retirada_id)
            if not retirada:
                logger.info(f"Retirada {retirada_id} não encontrada")
                return {"erro": "Retirada não encontrada"}, 404

            resposta = marshal(retirada, tb_retirada_fields)

            redis_client.setex(cache_key, 30, json.dumps(resposta))

            logger.info(f"Retirada {retirada_id} retornada do Banco de Dados!")
            return resposta, 200

        except SQLAlchemyError:
            logger.info(f"Erro SQLAlchemy ao buscar Retirada {retirada_id}")
            log_exception("Erro SQLAlchemy ao buscar Retirada")
            abort(500, description="Erro ao buscar Retirada no banco de dados")

        except Exception:
            logger.info("Erro inesperado ao buscar Retirada")
            log_exception("Erro inesperado ao buscar Retirada")
            abort(500, "Erro interno inesperado")                          

    def put(self, retirada_id):
        logger.info(f"PUT - Editando Retirada {retirada_id}")

        dados = request.get_json()
        schema = TB_RetiradaSchema()

        try:
            retirada = db.session.get(TB_Retirada, retirada_id)
            if not retirada:
                logger.info(f"Retirada {retirada_id} não encontrada")
                return {"erro": "Retirada não encontrada"}, 404
            
            status_anterior = retirada.status
            
            atualizados = schema.load(dados, partial=True)

            campos_permitidos = {"status", "hora_devolucao"}

            for campo, valor in atualizados.items():
                if campo in campos_permitidos:
                    setattr(retirada, campo, valor)

            if (
                status_anterior in ("retirada", "atrasada")
                and retirada.status == "devolvida"
            ):
                chave = db.session.get(TB_Chave, retirada.chave_id)
                sala = db.session.get(TB_Sala, chave.sala_id)

                retirada_ativa = (
                    db.session.query(TB_Retirada)
                    .join(TB_Chave)
                    .filter(
                        TB_Chave.sala_id == sala.sala_id,
                        TB_Retirada.status.in_(["retirada", "atrasada"])
                    )
                    .first()
                )

                if not retirada_ativa:
                    sala.disponivel = True
                    chave.disponivel = True
            db.session.commit()

            redis_client.delete(f"retirada:{retirada_id}")
            redis_client.delete_pattern("historico:*")

            return marshal(retirada, tb_retirada_fields), 200
        
        except ValidationError as err:
            logger.info(f"Dados inválidos, detalhes: {err.messages}")
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422
        
        except SQLAlchemyError:
            logger.info(f"Erro SQLAlchemy ao atualizar Retirada")
            log_exception("Erro SQLAlchemy ao atualizar Retirada")
            db.session.rollback()
            abort(500, description="Erro ao atualizar Retirada.")

        except Exception:
            logger.info("Erro inesperado ao atualizar Retirada")
            log_exception("Erro inesperado ao atualizar Retirada")
            abort(500, description="Erro interno inesperado.")  

    def delete(self, retirada_id):
        logger.info("DELETE - Apagando Retirada")

        try:
            retirada = db.session.get(TB_Retirada, retirada_id)
            if not retirada:
                logger.info(f"Retirada {retirada_id} não encontrada")
                return {"erro":"Retirada não encontrada"}, 404
            if retirada.status == "retirada" or retirada.status == "atrasada":
                logger.info(f"A retirada {retirada_id}ainda não foi finalizada, por isso não poderá ser deletada")
                return {"erro":"Retirada ainda não foi finalizada, por isso não poderá ser deletada"}, 409
            
            db.session.delete(retirada)
            db.session.commit()
            
            redis_client.delete(f"retirada:{retirada_id}")

            return {"mensagem":"Retirada removida com sucesso"}, 200
        
        except SQLAlchemyError:
            logger.info("Erro SQLAlchemy ao remover Retirada")
            log_exception("Erro SQLAlchemy ao remover Retirada")
            db.session.rollback()
            abort(500, description="Erro ao remover Retirada.")

        except Exception:
            logger.info("Erro inesperado ao remover Retirada")
            log_exception("Erro inesperado ao remover Retirada")
            abort(500, "Erro interno inesperado.")