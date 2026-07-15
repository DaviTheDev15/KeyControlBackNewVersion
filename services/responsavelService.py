import json
from flask_restful import marshal
from helpers.redis_cache import redis_client
from helpers.logging import logger
from helpers.auxiliaryFunctionsResources.redisCacheFunctions import (
    preencherRedisCache,
    verificarRedisCache
)
from helpers.auxiliaryFunctionsResources.solrFunctions import (
    adicionarResponsavel,
    deletarResponsavel,
    solrVerificationResponsavel
)
from helpers.auxiliaryFunctionsResources.mascararCampos import (
    mascarar_campos,
    mascarar_campos_item
)
from helpers.auxiliaryFunctionsResources.helpFunctionsForSql import aplicar_ordenacao
from helpers.auxiliaryFunctionsResources.genericValidationsForResource import (
    responsavelVerification,
    responsavelIsActive
)
from helpers.database import db
from models.Responsavel import (
    TB_Responsavel,
    tb_responsavel_fields
)
from repositories.responsavelRepository import ResponsavelRepository


class ResponsavelService:

    @staticmethod
    def listar(text):

        if text and text != "*":
            return solrVerificationResponsavel(text)

        cache_key = "responsaveis:*"

        cache = verificarRedisCache(
            "Responsaveis",
            cache_key
        )

        if cache:
            logger.info("Retornando responsáveis do Redis.")
            return json.loads(cache)

        query = db.select(TB_Responsavel)

        query = aplicar_ordenacao(
            query,
            {
                "id": TB_Responsavel.responsavel_id,
                "nome": TB_Responsavel.responsavel_nome,
                "ativo": TB_Responsavel.ativo
            },
            "id"
        )

        responsaveis = ResponsavelRepository.get_all(query)

        resposta = marshal(
            responsaveis,
            tb_responsavel_fields
        )

        mascarar_campos(
            resposta,
            [
                "responsavel_cpf",
                "responsavel_siap",
                "responsavel_matricula"
            ]
        )

        preencherRedisCache(
            cache_key,
            resposta
        )

        logger.info("Retornando responsáveis do Banco de Dados.")
        return resposta


    @staticmethod
    def buscar_por_id(responsavel_id):

        cache_key = f"responsaveis:{responsavel_id}"

        cache = verificarRedisCache(
            "Responsavel",
            cache_key
        )

        if cache:
            logger.info("Retornando responsáveis do Redis.")
            return json.loads(cache)

        responsavel = ResponsavelRepository.get_by_id(
            responsavel_id
        )

        responsavelVerification(
            responsavel_id
        )

        resposta = marshal(
            responsavel,
            tb_responsavel_fields
        )

        mascarar_campos_item(
            resposta,
            [
                "responsavel_cpf",
                "responsavel_siap",
                "responsavel_matricula"
            ]
        )

        preencherRedisCache(
            cache_key,
            resposta
        )
        logger.info("Retornando responsáveis do Banco de Dados.")
        return resposta


    @staticmethod
    def criar(validado):

        senha = validado.pop("senha")

        primeiro = ResponsavelRepository.first() is None

        funcao = "admin" if primeiro else "responsavel"

        responsavel = TB_Responsavel(
            **validado,
            funcao=funcao
        )

        responsavel.set_senha(senha)

        ResponsavelRepository.save(responsavel)

        adicionarResponsavel(responsavel)

        redis_client.delete_pattern("responsaveis:*")

        return responsavel


    @staticmethod
    def atualizar(responsavel_id, atualizados):

        responsavel = ResponsavelRepository.get_by_id(
            responsavel_id
        )

        responsavelVerification(
            responsavel_id
        )

        for campo, valor in atualizados.items():
            setattr(
                responsavel,
                campo,
                valor
            )

        ResponsavelRepository.update()

        adicionarResponsavel(responsavel)

        redis_client.delete_pattern("responsaveis:*")

        return responsavel


    @staticmethod
    def remover(responsavel_id):

        responsavel = ResponsavelRepository.get_by_id(
            responsavel_id
        )

        responsavelVerification(
            responsavel_id
        )

        responsavelIsActive(
            responsavel_id
        )

        ResponsavelRepository.delete(
            responsavel
        )

        deletarResponsavel(
            responsavel_id
        )

        redis_client.delete_pattern("responsaveis:*")
        