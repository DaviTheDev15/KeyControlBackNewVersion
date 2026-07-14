import json
from flask_restful import marshal
from helpers.database import db
from helpers.redis_cache import redis_client
from helpers.logging import logger
from helpers.auxiliaryFunctionsResources.helpFunctionsForSql import aplicar_ordenacao
from helpers.auxiliaryFunctionsResources.redisCacheFunctions import (
    verificarRedisCache,
    preencherRedisCache
)
from helpers.auxiliaryFunctionsResources.solrFunctions import (
    adicionarSala,
    deletarSala,
    solrVerificationSala
)
from helpers.auxiliaryFunctionsResources.genericValidationsForResource import (
    salaVerification
)
from models.TB_Sala import (
    TB_Sala,
    tb_sala_fields
)
from models.TB_Chave import TB_Chave
from repositories.sala_repository import SalaRepository


class SalaService:

    @staticmethod
    def listar(text):

        if text and text != "*":
            return solrVerificationSala(text)

        cache_key = "salas:*"

        cache = verificarRedisCache(
            "Salas",
            cache_key
        )

        if cache:
            logger.info("Retornando salas do Redis.")
            return json.loads(cache)

        query = db.select(TB_Sala)

        query = aplicar_ordenacao(
            query,
            {
                "id": TB_Sala.sala_id,
                "nome": TB_Sala.sala_nome,
                "disponivel": TB_Sala.disponivel
            },
            "id"
        )

        salas = SalaRepository.get_all(query)

        resposta = marshal(
            salas,
            tb_sala_fields
        )

        preencherRedisCache(
            cache_key,
            resposta
        )

        logger.info("Retornando salas do Banco de Dados.")
        return resposta


    @staticmethod
    def buscar_por_id(sala_id):

        cache_key = f"salas:{sala_id}"

        cache = verificarRedisCache(
            "Salas",
            cache_key
        )

        if cache:
            logger.info("Retornando salas do Redis.")
            return json.loads(cache)

        sala = SalaRepository.get_by_id(sala_id)

        salaVerification(sala_id)

        resposta = marshal(
            sala,
            tb_sala_fields
        )

        preencherRedisCache(
            cache_key,
            resposta
        )

        logger.info("Retornando salas do Banco de Dados.")
        return resposta


    @staticmethod
    def criar(validado):

        sala = TB_Sala(**validado)

        SalaRepository.save(sala)

        adicionarSala(sala)

        redis_client.delete_pattern("salas:*")

        return sala


    @staticmethod
    def atualizar(sala_id, atualizados):

        sala = SalaRepository.get_by_id(sala_id)

        salaVerification(sala_id)

        nome_antigo = sala.sala_nome

        for campo, valor in atualizados.items():
            setattr(
                sala,
                campo,
                valor
            )

        if (
            "sala_nome" in atualizados
            and nome_antigo != sala.sala_nome
        ):

            chaves = SalaRepository.get_chaves_da_sala(
                sala.sala_id
            )

            for indice, chave in enumerate(chaves, start=1):

                chave.chave_nome = (
                    f"Chave {sala.sala_nome} {indice:02d}"
                )

        SalaRepository.update()

        adicionarSala(sala)

        redis_client.delete_pattern("salas:*")

        return sala


    @staticmethod
    def remover(sala_id):

        sala = SalaRepository.get_by_id(
            sala_id
        )

        salaVerification(
            sala_id
        )

        SalaRepository.delete(
            sala
        )

        deletarSala(
            sala_id
        )

        redis_client.delete_pattern(
            "salas:*"
        )