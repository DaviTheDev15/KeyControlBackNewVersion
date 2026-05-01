from flask import request, abort
from flask_restful import Resource, marshal
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from helpers.database import db
from helpers.logging import logger, log_exception
from helpers.redis_cache import redis_client
from helpers.auxiliaryFunctionsResources.helpFunctionsForReservaResources import existe_conflito_reserva_raw, merge_reserva
from helpers.auxiliaryFunctionsResources.redisCacheFunctions import verificarRedisCache, preencherRedisCache
from helpers.auxiliaryFunctionsResources.genericValidationsForResource import salaVerification, responsavelIsActive, responsavelVerification, reservaVerification, reservaStatusIsAtiva
from models.TB_Reserva import TB_Reserva, TB_ReservaSchema, tb_reserva_fields
from models.TB_ReservaDia import TB_ReservaDia
from werkzeug.exceptions import HTTPException   

import json

class TB_ReservasResource(Resource):
    def get(self):
        logger.info("GET ALL - Listagem de Reservas")

        try:
            cachekey = "reservas:*"

            cache = verificarRedisCache("Reservas", cachekey)

            if cache:
                logger.info("Retornando Reservas do Redis")
                return json.loads(cache), 200
            
        except Exception:
            log_exception("Erro ao retornar Reservas do Redis Cache")
            abort(500, "Erro ao retornar Reservas do Redis Cache")

        try:
            logger.info("Redis Cache vazio!")
            logger.info("Buscando Reservas no Banco de Dados!")

            query = db.select(TB_Reserva).order_by(TB_Reserva.reserva_id)

            reservas = db.session.execute(query).scalars().all()

            resposta = marshal(reservas, tb_reserva_fields)

            preencherRedisCache(cachekey, resposta)

            logger.info("Retornando Reservas do Banco de Dados")

            return resposta, 200

        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao buscar TB_Reservas")
            db.session.rollback()
            abort(500, "Erro ao buscar TB_Reservas no banco de dados")

        except HTTPException:
            raise

        except Exception:
            log_exception("Erro inesperado ao buscar TB_Reservas")
            abort(500, description="Erro interno inesperado.")

    def post(self):
        logger.info("POST - Nova Reserva")

        dados = request.get_json()

        schema = TB_ReservaSchema()
        try:
            validado = schema.load(dados)

            dias_semana = validado.pop("dias_semana", [])

            if validado["frequencia"] == "única":
                validado["data_fim"] = validado["data_inicio"]

            salaVerification(validado["sala_id"])

            responsavelVerification(validado["responsavel_id"])

            responsavelIsActive(validado["responsavel_id"])

            if existe_conflito_reserva_raw(
                sala_id=validado["sala_id"],
                hora_inicio=validado["hora_inicio"],
                hora_fim=validado["hora_fim"],
                data_inicio=validado["data_inicio"],
                dias_semana=dias_semana
            ):
                logger.info("Há um conflito de reserva, já existe uma reserva ativa para esta sala no mesmo horário e dia da semana!")
                return {
                    "erro": "Conflito de reserva",
                    "mensagem": "Já existe reserva ativa para esta sala no mesmo horário e dia da semana."
                }, 409

            reserva = TB_Reserva(**validado)

            db.session.add(reserva)
            
            db.session.flush()

            for dia in dias_semana:
                reserva.tb_reserva_dia.append(TB_ReservaDia(dia_semana=dia))
            
            db.session.add(reserva)

            db.session.commit()

            redis_client.delete_pattern("reservas:*")

            return marshal(reserva, tb_reserva_fields), 201

        except ValidationError as err:
            logger.info(f"Dados inválidos, detalhes {err.messages}")
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422

        except SQLAlchemyError:
            logger.info("Erro SQLAlchemy ao inserir Reserva")
            log_exception("Erro SQLAlchemy ao criar Reserva")
            db.session.rollback()
            abort(500, "Erro ao criar Reserva")

        except HTTPException:
            raise

        except Exception:
            logger.info("Erro inesperado ao inserir Reserva")
            log_exception("Erro inesperado ao inserir Reserva")
            abort(500, "Erro interno Reserva.")

class TB_ReservaResource(Resource):

    def get(self, reserva_id):
        logger.info(f"GET - Reserva {reserva_id}")

        try:
            cacheKey = f"reservas:{reserva_id}"

            cache = verificarRedisCache("Reservas", cacheKey)

            if cache:
                logger.info(f"Retornando reserva {reserva_id} do Redis!")                
                return json.loads(cache), 200
            
        except Exception:
            logger.info("Erro ao acessar o Redis Cache")            
            log_exception("Erro ao acessar Redis")
            abort(500, description="Erro ao acessar o Redis Cache")

        try:
            logger.info("Redis Cache estava vazio!")
            logger.info("Buscando no Banco de Dados!")

            reserva = db.session.get(TB_Reserva, reserva_id)

            reservaVerification(reserva_id)

            resposta = marshal(reserva, tb_reserva_fields)

            preencherRedisCache(resposta)

            logger.info(f"Reserva {reserva_id} retornado do Banco de Dados!")

            return resposta, 200

        except SQLAlchemyError:
            logger.info(f"Erro SQLAlchemy ao buscar Reserva {reserva_id}")
            log_exception("Erro SQLAlchemy ao buscar Reserva")
            abort(500, description="Erro ao buscar Reserva no banco de dados")

        except HTTPException:
            raise

        except Exception:
            logger.info("Erro inesperado ao buscar Reserva")
            log_exception("Erro inesperado ao buscar Reserva")
            abort(500, "Erro interno inesperado")        

    def put(self, reserva_id):
        logger.info(f"PUT - Editando Reserva {reserva_id}")

        reserva = db.session.get(TB_Reserva, reserva_id)

        reservaVerification(reserva_id)
        
        dados = request.get_json()

        dias_payload = dados.pop("dias_semana", None)

        frequencia_final = dados.get("frequencia", reserva.frequencia)

        if frequencia_final in ("única", "mensal"):
            dias_finais = []
        else:
            if dias_payload is None:
                dias_finais = [d.dia_semana for d in reserva.tb_reserva_dia]
            else:
                dias_finais = dias_payload

        
        dados["frequencia"] = frequencia_final

        dados["dias_semana"] = dias_finais


        schema = TB_ReservaSchema()

        try:
            
            dados_normalizados = schema.load(dados, partial=True)

            dados_finais = merge_reserva(reserva, dados_normalizados)

            if existe_conflito_reserva_raw(
                sala_id=dados_finais["sala_id"],
                hora_inicio=dados_finais["hora_inicio"],
                hora_fim=dados_finais["hora_fim"],
                data_inicio=dados_finais["data_inicio"],
                dias_semana=dias_finais,
                reserva_id_excluir=reserva_id
            ):
                logger.info("Há um conflito de reserva, as alterações feitas na reserva geram conflito com outra reserva existente.")
                return {
                    "erro": "Conflito de reserva",
                    "mensagem": "Alteração gera conflito com outra reserva existente."
                }, 409
                
            atualizados = dados_normalizados

            for campo, valor in atualizados.items():
                setattr(reserva, campo, valor)

            db.session.query(TB_ReservaDia)\
                .filter_by(reserva_id=reserva_id)\
                .delete()

            for dia in dias_finais:
                db.session.add(
                    TB_ReservaDia(
                        reserva_id=reserva_id,
                        dia_semana=dia
                    )
                )

            db.session.commit()

            redis_client.delete_pattern("reservas:*")

            return marshal(reserva, tb_reserva_fields), 200

        except ValidationError as err:
            logger.info(f"Dados inválidos, detalhes: {err.messages}")
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422

        except SQLAlchemyError:
            logger.info(f"Erro SQLAlchemy ao atualizar Reserva {reserva_id}")
            log_exception("Erro SQLAlchemy ao atualizar Reserva")
            db.session.rollback()
            abort(500, description="Erro ao atualizar Reserva.")

        except HTTPException:
            raise

        except Exception:
            logger.info(f"Erro inesperado ao atualizar Reserva {reserva_id}")
            log_exception("Erro inesperado ao atualizar Reserva")
            abort(500, description="Erro interno inesperado.")

    def delete(self, reserva_id):
        logger.info(f"DELETE - Apagando Reserva {reserva_id}")

        try:
            reserva = db.session.get(TB_Reserva, reserva_id)

            reservaVerification(reserva_id)

            reservaStatusIsAtiva(reserva_id)
            
            db.session.delete(reserva)

            db.session.commit()

            redis_client.delete_pattern("reservas:*")

            return {"mensagem": "Reserva apagada com sucesso"}, 200

        except SQLAlchemyError:
            logger.info(f"Erro SQLAlchemy ao remover Reserva {reserva_id}")
            log_exception("Erro SQLAlchemy ao cancelar Reserva")
            db.session.rollback()
            abort(500, description="Erro ao remover Reserva.")

        except HTTPException:
            raise

        except Exception:
            logger.info("Erro inesperado ao remover Reserva")
            log_exception("Erro inesperado ao remover Reserva")
            abort(500, "Erro interno inesperado.")  