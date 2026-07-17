import json
from flask_restful import marshal
from helpers.database import db
from helpers.redis_cache import redis_client
from helpers.logging import logger
from helpers.auxiliaryFunctionsResources.redisCacheFunctions import (
    verificarRedisCache,
    preencherRedisCache
)
from helpers.auxiliaryFunctionsResources.helpFunctionsForSql import (
    aplicar_ordenacao
)
from helpers.auxiliaryFunctionsResources.helpFunctionsForReservaResources import (
    existe_conflito_reserva_raw,
    merge_reserva
)
from helpers.auxiliaryFunctionsResources.genericValidationsForResource import (
    salaVerification,
    responsavelVerification,
    reservaVerification,
    reservaStatusIsAtivaInDelete
)
from models.Reserva import (
    TB_Reserva,
    tb_reserva_fields
)

from repositories.reservaRepository import ReservaRepository
from models.ReservaDia import TB_ReservaDia

class ReservaService:

    @staticmethod
    def listar():

        cache_key = "reservas:*"

        cache = verificarRedisCache(
            "Reservas",
            cache_key
        )

        if cache:
            logger.info("Retornando Reservas do Redis.")
            return json.loads(cache)

        query = db.select(TB_Reserva)

        query = aplicar_ordenacao(
            query,
            {
                "id": TB_Reserva.reserva_id,
                "sala": TB_Reserva.sala_id,
                "responsavel": TB_Reserva.responsavel_id,
                "data": TB_Reserva.data_inicio,
                "frequencia": TB_Reserva.frequencia,
                "status": TB_Reserva.status
            },
            "id"
        )

        reservas = ReservaRepository.get_all(query)

        resposta = marshal(
            reservas,
            tb_reserva_fields
        )

        preencherRedisCache(
            cache_key,
            resposta
        )

        logger.info("Retornando Reservas do Banco de Dados.")
        return resposta


    @staticmethod
    def buscar_por_id(reserva_id):

        cache_key = f"reservas:{reserva_id}"

        cache = verificarRedisCache(
            "Reservas",
            cache_key
        )

        if cache:
            logger.info("Retornando Reservas do Redis.")
            return json.loads(cache)

        reserva = ReservaRepository.get_by_id(
            reserva_id
        )

        reservaVerification(
            reserva_id
        )

        resposta = marshal(
            reserva,
            tb_reserva_fields
        )

        preencherRedisCache(
            cache_key,
            resposta
        )

        logger.info("Retornando Reservas do Banco de Dados.")
        return resposta


    @staticmethod
    def criar(validado):

        dias_semana = validado.pop(
            "dias_semana",
            []
        )

        if validado["frequencia"] == "única":
            validado["data_fim"] = validado["data_inicio"]

        salaVerification(
            validado["sala_id"]
        )

        responsavelVerification(
            validado["responsavel_id"]
        )

        if existe_conflito_reserva_raw(
            sala_id=validado["sala_id"],
            hora_inicio=validado["hora_inicio"],
            hora_fim=validado["hora_fim"],
            data_inicio=validado["data_inicio"],
            dias_semana=dias_semana
        ):
            return {
                "erro": "Conflito de reserva",
                "mensagem": (
                    "Já existe reserva ativa para esta sala "
                    "no mesmo horário e dia da semana."
                )
            }, 409

        reserva = TB_Reserva(**validado)

        db.session.add(reserva)

        ReservaRepository.flush()

        for dia in dias_semana:
            reserva.tb_reserva_dia.append(
                TB_ReservaDia(
                    dia_semana=dia
                )
        )

        ReservaRepository.update()

        redis_client.delete_pattern(
            "reservas:*"
        )

        return reserva


    @staticmethod
    def atualizar(reserva_id, dados):

        reserva = ReservaRepository.get_by_id(
            reserva_id
        )

        reservaVerification(
            reserva_id
        )

        dias_payload = dados.pop(
            "dias_semana",
            None
        )

        frequencia_final = dados.get(
            "frequencia",
            reserva.frequencia
        )

        if frequencia_final in (
            "única",
            "mensal"
        ):
            dias_finais = []

        else:
            if dias_payload is None:
                dias_finais = [
                    d.dia_semana
                    for d in reserva.tb_reserva_dia
                ]
            else:
                dias_finais = dias_payload

        dados["frequencia"] = frequencia_final
        dados["dias_semana"] = dias_finais

        dados_finais = merge_reserva(
            reserva,
            dados
        )

        if existe_conflito_reserva_raw(
            sala_id=dados_finais["sala_id"],
            hora_inicio=dados_finais["hora_inicio"],
            hora_fim=dados_finais["hora_fim"],
            data_inicio=dados_finais["data_inicio"],
            dias_semana=dias_finais,
            reserva_id_excluir=reserva_id
        ):
            return {
                "erro": "Conflito de reserva",
                "mensagem": (
                    "Alteração gera conflito com outra "
                    "reserva existente."
                )
            }, 409

        for campo, valor in dados.items():

            if campo != "dias_semana":
                setattr(
                    reserva,
                    campo,
                    valor
                )

        ReservaRepository.limpar_dias_semana(
            reserva_id
        )

        for dia in dias_finais:
            ReservaRepository.adicionar_dia(
                reserva_id,
                dia
            )

        ReservaRepository.update()

        redis_client.delete_pattern(
            "reservas:*"
        )

        return reserva


    @staticmethod
    def remover(reserva_id):

        reserva = ReservaRepository.get_by_id(
            reserva_id
        )

        reservaVerification(
            reserva_id
        )

        reservaStatusIsAtivaInDelete(
            reserva_id
        )

        ReservaRepository.delete(
            reserva
        )

        redis_client.delete_pattern(
            "reservas:*"
        )