import json
from flask_restful import marshal
from helpers.database import db
from helpers.logging import logger
from helpers.redis_cache import redis_client
from helpers.auxiliaryFunctionsResources.helpFunctionsForSql import aplicar_ordenacao
from helpers.auxiliaryFunctionsResources.helpFunctionsForChavesResources import gerar_nome_da_chave
from helpers.auxiliaryFunctionsResources.redisCacheFunctions import (
    verificarRedisCache,
    preencherRedisCache
)
from helpers.auxiliaryFunctionsResources.genericValidationsForResource import (
    salaVerification,
    chaveVerification
)
from models.TB_Chave import (
    TB_Chave,
    tb_chave_fields
)
from repositories.chave_repository import ChaveRepository


class ChaveService:

    @staticmethod
    def listar():

        cache_key = "chaves:*"

        cache = verificarRedisCache(
            "Chaves",
            cache_key
        )

        if cache:
            logger.info("Retornando Chaves do Redis.")
            return json.loads(cache)

        query = db.select(TB_Chave)

        query = aplicar_ordenacao(
            query,
            {
                "id": TB_Chave.chave_id,
                "nome": TB_Chave.chave_nome,
                "disponivel": TB_Chave.disponivel
            },
            "id"
        )

        chaves = ChaveRepository.get_all(query)

        resposta = marshal(
            chaves,
            tb_chave_fields
        )

        preencherRedisCache(
            cache_key,
            resposta
        )

        return resposta


    @staticmethod
    def buscar_por_id(chave_id):

        cache_key = f"chaves:{chave_id}"

        cache = verificarRedisCache(
            "Chaves",
            cache_key
        )

        if cache:
            return json.loads(cache)

        chave = ChaveRepository.get_by_id(
            chave_id
        )

        chaveVerification(
            chave_id
        )

        resposta = marshal(
            chave,
            tb_chave_fields
        )

        preencherRedisCache(
            cache_key,
            resposta
        )

        return resposta


    @staticmethod
    def criar(validado):

        salaVerification(
            validado["sala_id"]
        )

        nome = gerar_nome_da_chave(
            validado["sala_id"]
        )

        chave = TB_Chave(
            chave_nome=nome,
            sala_id=validado["sala_id"],
            disponivel=validado["disponivel"]
        )

        ChaveRepository.save(
            chave
        )

        redis_client.delete_pattern(
            "chaves:*"
        )

        return chave


    @staticmethod
    def atualizar(chave_id, atualizados):

        chave = ChaveRepository.get_by_id(
            chave_id
        )

        chaveVerification(
            chave_id
        )

        if "sala_id" in atualizados:
            salaVerification(
                atualizados["sala_id"]
            )

        for campo, valor in atualizados.items():
            setattr(
                chave,
                campo,
                valor
            )

        ChaveRepository.update()

        redis_client.delete_pattern(
            "chaves:*"
        )

        return chave


    @staticmethod
    def remover(chave_id):

        chave = ChaveRepository.get_by_id(
            chave_id
        )

        chaveVerification(
            chave_id
        )

        if not chave.disponivel:
            return {
                "erro": "Chave está em uso, não pode ser removida"
            }, 400

        ChaveRepository.delete(
            chave
        )

        redis_client.delete_pattern(
            "chaves:*"
        )