from flask import request, abort
from flask_restful import Resource, marshal
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from helpers.database import db
from helpers.logging import logger, log_exception
from helpers.redis_cache import redis_client

from models.TB_Reserva import TB_Reserva, TB_ReservaSchema, tb_reserva_fields
from models.TB_ReservaDia import TB_ReservaDia
from models.TB_Sala import TB_Sala
from models.TB_Responsavel import TB_Responsavel

import json

def existe_conflito_reserva_raw(
    sala_id,
    hora_inicio,
    hora_fim,
    data_inicio,
    dias_semana,
    reserva_id_excluir=None
):
    dia_semana = data_inicio.weekday() + 1
    dia_mes = data_inicio.day

    sql = text("""
        SELECT 1
        FROM tb_reserva r
        LEFT JOIN tb_reserva_dia d ON d.reserva_id = r.reserva_id
        WHERE r.status = 'ativa'
          AND r.sala_id = :sala_id
          AND (:hora_inicio < r.hora_fim AND :hora_fim > r.hora_inicio)
          AND r.data_inicio <= :data_inicio
          AND (r.data_fim IS NULL OR r.data_fim >= :data_inicio)
          AND (
                -- 🔹 semanal
                (r.frequencia = 'semanal' AND d.dia_semana = :dia_semana)

                -- 🔹 mensal
                OR (r.frequencia = 'mensal' AND EXTRACT(DAY FROM r.data_inicio) = :dia_mes)

                -- 🔹 única
                OR (r.frequencia = 'única' AND r.data_inicio = :data_inicio)
          )
          AND (:reserva_id_excluir IS NULL OR r.reserva_id <> :reserva_id_excluir)
        LIMIT 1
    """)

    params = {
        "sala_id": sala_id,
        "hora_inicio": hora_inicio,
        "hora_fim": hora_fim,
        "data_inicio": data_inicio,
        "dia_semana": dia_semana,
        "dia_mes": dia_mes,
        "reserva_id_excluir": reserva_id_excluir
    }

    return db.session.execute(sql, params).fetchone() is not None


def merge_reserva(reserva, dados):
    return {
        "sala_id": dados.get("sala_id", reserva.sala_id),
        "responsavel_id": dados.get("responsavel_id", reserva.responsavel_id),
        "hora_inicio": dados.get("hora_inicio", reserva.hora_inicio),
        "hora_fim": dados.get("hora_fim", reserva.hora_fim),
        "data_inicio": dados.get("data_inicio", reserva.data_inicio),
        "data_fim": dados.get("data_fim", reserva.data_fim),
        "frequencia": dados.get("frequencia", reserva.frequencia),
        "status": dados.get("status", reserva.status),
    }


class TB_ReservasResource(Resource):
    def get(self):
        logger.info("GET ALL - Listagem de Reservas")

        try:
            cache_key = "reservas:all"
            cache = redis_client.get(cache_key)

            logger.info("Verificando se há dados das Reservas no Redis!")
            if cache:
                logger.info("Retornando Reservas do Redis")
                return json.loads(cache), 200
            
        except Exception:
            logger.info("Erro ao acessar o Redis Cache")
            log_exception("Erro ao acessar Redis")
            abort(500, "Erro ao acessar cache")

        try:
            logger.info("Redis Cache estava vazio!")
            logger.info("Buscando no Banco de Dados!")
            query = db.select(TB_Reserva).order_by(TB_Reserva.reserva_id)
            reservas = db.session.execute(query).scalars().all()

            resposta = marshal(reservas, tb_reserva_fields)

            redis_client.setex(cache_key, 30, json.dumps(resposta))
            logger.info("Retornando Reservas do Banco de Dados")
            return resposta, 200

        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao buscar TB_Reservas")
            logger.info("Erro SQLAlchemy ao buscar TB_Reservas")
            db.session.rollback()
            abort(500, "Erro ao buscar TB_Reservas no banco de dados")

        except Exception:
            log_exception("Erro inesperado ao buscar TB_Reservas")
            logger.info("Erro inesperado ao buscar TB_Reservas")
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
            sala = db.session.get(TB_Sala, validado["sala_id"])

            if not sala:
                logger.info(f"Sala não encontrada, não será possivel cadastrar uma nova reserva para ela")
                return {"erro": "Sala não encontrada"}, 404

            responsavel = db.session.get(TB_Responsavel, validado["responsavel_id"])
            if not responsavel or not responsavel.ativo:
                logger.info(f"Responsável não encontrado ou inativo, não será possivel cadastrar uma nova reserva para ele")
                return {"erro": "Responsável inválido ou inativo"}, 400
            
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

        except Exception:
            logger.info("Erro inesperado ao inserir Reserva")
            log_exception("Erro inesperado ao inserir Reserva")
            abort(500, "Erro interno Reserva.")

class TB_ReservaResource(Resource):

    def get(self, reserva_id):
        logger.info(f"GET - Reserva {reserva_id}")

        try:
            cache_key = f"reserva:{reserva_id}"
            logger.info(f"Verificando se há dados da reserva {reserva_id} no Redis")
            cache = redis_client.get(cache_key)
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
            if not reserva:
                logger.info(f"Reserva {reserva_id} não encontrada")
                return {"erro": "Reserva não encontrada"}, 404

            resposta = marshal(reserva, tb_reserva_fields)

            redis_client.setex(cache_key, 30, json.dumps(resposta))
            logger.info(f"Reserva {reserva_id} retornado do Banco de Dados!")
            return resposta, 200

        except SQLAlchemyError:
            logger.info(f"Erro SQLAlchemy ao buscar Reserva {reserva_id}")
            log_exception("Erro SQLAlchemy ao buscar Reserva")
            abort(500, description="Erro ao buscar Reserva no banco de dados")
        
        except Exception:
            logger.info("Erro inesperado ao buscar Reserva")
            log_exception("Erro inesperado ao buscar Reserva")
            abort(500, "Erro interno inesperado")        

    def put(self, reserva_id):
        logger.info(f"PUT - Editando Reserva {reserva_id}")

        reserva = db.session.get(TB_Reserva, reserva_id)
        if not reserva:
            logger.info(f"Reserva não encontrada")
            return {"erro": "Reserva não encontrada"}, 404
        
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
            redis_client.delete_pattern("reserva:*")

            return marshal(reserva, tb_reserva_fields), 200

        except ValidationError as err:
            logger.info(f"Dados inválidos, detalhes: {err.messages}")
            return {"erro": "Dados inválidos", "detalhes": err.messages}, 422

        except SQLAlchemyError:
            logger.info(f"Erro SQLAlchemy ao atualizar Reserva {reserva_id}")
            log_exception("Erro SQLAlchemy ao atualizar Reserva")
            db.session.rollback()
            abort(500, description="Erro ao atualizar Reserva.")

        except Exception:
            logger.info(f"Erro inesperado ao atualizar Reserva {reserva_id}")
            log_exception("Erro inesperado ao atualizar Reserva")
            abort(500, description="Erro interno inesperado.")

    def delete(self, reserva_id):
        logger.info(f"DELETE - Apagando Reserva {reserva_id}")

        try:
            reserva = db.session.get(TB_Reserva, reserva_id)
            if not reserva:
                logger.info(f"Reserva {reserva_id} não encontrada")
                return {"erro": "Reserva não encontrada"}, 404
            if reserva.status == "ativa":
                logger.info(f"Reserva {reserva_id} está ativa, não pode ser apagada!")
                return {"erro": "Não é possível apagar uma reserva que se encontra ativa"}, 409
            
            db.session.delete(reserva)
            db.session.commit()

            redis_client.delete_pattern("reserva:*")

            return {"mensagem": "Reserva apagada com sucesso"}, 200

        except SQLAlchemyError:
            logger.info(f"Erro SQLAlchemy ao remover Reserva {reserva_id}")
            log_exception("Erro SQLAlchemy ao cancelar Reserva")
            db.session.rollback()
            abort(500, description="Erro ao remover Reserva.")

        except Exception:
            logger.info("Erro inesperado ao remover Reserva")
            log_exception("Erro inesperado ao remover Reserva")
            abort(500, "Erro interno inesperado.")  