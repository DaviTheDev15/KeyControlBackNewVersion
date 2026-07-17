from datetime import date, datetime, timedelta
import json
from flask import abort
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
from helpers.auxiliaryFunctionsResources.genericValidationsForResource import (
    chaveIsDisponivel,
    chaveVerification,
    reservaStatusIsAtiva,
    responsavelNotActive,
    salaVerification,
    responsavelVerification,
    reservaVerification,
    reservaStatusIsAtivaInDelete,
    retiradaVerification,
    retiradaStatus
)
from models.Retirada import (
    TB_Retirada,
    tb_retirada_fields
)

from repositories.chaveRepository import ChaveRepository
from repositories.reservaRepository import ReservaRepository
from repositories.retiradaRepository import RetiradaRepository
from repositories.salaRepository import SalaRepository

class RetiradaService:
    @staticmethod
    def listar():
        cache_key = "retiradas:*"

        cache = verificarRedisCache("Retiradas", cache_key)
        if cache:
            return json.loads(cache)

        query = db.select(TB_Retirada)

        query = aplicar_ordenacao(
            query,
            {
                "id": TB_Retirada.retirada_id,
                "chave": TB_Retirada.chave_id,
                "responsavel": TB_Retirada.responsavel_id,
                "reserva": TB_Retirada.reserva_id,
                "data": TB_Retirada.data_retirada,
                "status": TB_Retirada.status,
            },
            "id"
        )

        retiradas = RetiradaRepository.get_all(query)

        resposta = marshal(retiradas, tb_retirada_fields)

        preencherRedisCache(cache_key, resposta)

        return resposta
    

    @staticmethod
    def buscar_por_id(retirada_id):
        cache_key = f"retiradas:{retirada_id}"

        cache = verificarRedisCache("Retiradas", cache_key)

        if cache:
            return json.loads(cache)

        retirada = RetiradaRepository.get_by_id(retirada_id)

        retiradaVerification(retirada_id)

        resposta = marshal(retirada, tb_retirada_fields)

        preencherRedisCache(cache_key, resposta)

        return resposta
    

    @staticmethod
    def criar(validado):
        hoje = date.today()

        chaveVerification(validado["chave_id"])

        chave = ChaveRepository.get_by_id(validado["chave_id"])

        chaveIsDisponivel(validado["chave_id"])

        sala = SalaRepository.get_by_id(chave.sala_id)

        if validado.get("reserva_id") is not None:

            reservaVerification(validado["reserva_id"])
            reservaStatusIsAtiva(validado["reserva_id"])

            reserva = ReservaRepository.get_by_id(validado["reserva_id"])

            if not (reserva.data_inicio <= hoje <= reserva.data_fim):
                abort(409, description="Hoje não está dentro do período da reserva")

            if reserva.frequencia not in ("única", "mensal"):

                dia_semana_hoje = hoje.isoweekday()

                dias_permitidos = [
                    d.dia_semana
                    for d in reserva.tb_reserva_dia
                ]

                if dia_semana_hoje not in dias_permitidos:
                    abort(
                        409,
                        description="Hoje não é um dia permitido pela reserva"
                    )

            hora_retirada = validado["hora_retirada"]

            hora_minima = (
                datetime.combine(
                    hoje,
                    reserva.hora_inicio
                ) - timedelta(minutes=10)
            ).time()

            if not (hora_minima <= hora_retirada <= reserva.hora_fim):
                abort(
                    409,
                    description="Retirada fora do intervalo permitido."
                )

            if reserva.sala_id != chave.sala_id:
                abort(
                    409,
                    description="Reserva não pertence à sala da chave."
                )

        if RetiradaRepository.get_retirada_ativa_da_sala(
            chave.sala_id
        ):
            abort(
                409,
                description="Já existe uma retirada ativa para esta sala."
            )

        responsavelVerification(validado["responsavel_id"])
        responsavelNotActive(validado["responsavel_id"])

        retirada = TB_Retirada(**validado)

        chave.disponivel = False
        sala.disponivel = False

        RetiradaRepository.save(retirada)

        redis_client.delete_pattern("retiradas:*")
        redis_client.delete_pattern("historicos:*")

        return retirada
    

    @staticmethod
    def atualizar(retirada_id, atualizados):

        retirada = RetiradaRepository.get_by_id(retirada_id)

        retiradaVerification(retirada_id)

        status_anterior = retirada.status

        campos_permitidos = {
            "status",
            "hora_devolucao"
        }

        for campo, valor in atualizados.items():

            if campo in campos_permitidos:
                setattr(retirada, campo, valor)

        if (
            status_anterior in ("retirada", "atrasada")
            and retirada.status == "devolvida"
        ):

            chave = ChaveRepository.get_by_id(retirada.chave_id)

            sala = SalaRepository.get_by_id(chave.sala_id)

            if not RetiradaRepository.get_retirada_ativa_da_sala(
                sala.sala_id
            ):
                chave.disponivel = True
                sala.disponivel = True

        RetiradaRepository.update()

        redis_client.delete_pattern("retiradas:*")
        redis_client.delete_pattern("historicos:*")

        return retirada
    

    @staticmethod
    def remover(retirada_id):

        retirada = RetiradaRepository.get_by_id(retirada_id)

        retiradaVerification(retirada_id)

        retiradaStatus(retirada_id)

        RetiradaRepository.delete(retirada)

        redis_client.delete_pattern("retiradas:*")
        redis_client.delete_pattern("historicos:*")