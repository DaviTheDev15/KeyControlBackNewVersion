from flask_restful import Resource
from sqlalchemy import text
from flask import request, abort, jsonify
from helpers.database import db
from helpers.logging import logger, log_exception
import json
from helpers.redis_cache import redis_client
from helpers.auxiliaryFunctionsResources.redisCacheFunctions import setCacheKey, verificarRedisCache, preencherRedisCache
from helpers.auxiliaryFunctionsResources.sqlRequestForHistory import sqlRequisicaoGetAll, sqlRequisicaoGetById

class HistoricoResource(Resource):
    def get(self):
        logger.info("GET ALL - Histórico de Retiradas")

        try:
            cacheKey = f"historico:{json.dumps(request.args, sort_keys=True)}"
            
            cache = verificarRedisCache("Historico de Retiradas", cacheKey)

            if cache:
                logger.info("Retornando Historico de Retiradas do Redis")
                return json.loads(cache), 200

        except Exception:
            log_exception("Erro ao retornar Historico de Retiradas do Redis Cache")
            abort(500, "Erro ao retornar Historico de Retiradas do Redis Cache")

        try:
            logger.info("Redis Cache vazio!")
            logger.info("Buscando Retiradas no Banco de Dados")

            resultado = sqlRequisicaoGetAll()

            preencherRedisCache(cacheKey, resultado)

            logger.info("Retornando o Historico de Retiradas do Banco de Dados")
            return resultado, 200

        except Exception:
            log_exception("Erro ao retornar Historico de Retiradas do Banco de Dados")
            abort(500, "Erro ao retornar Historico de Retiradas do Banco de Dados")


class HistoricoByIdResource(Resource):
    def get(self, retirada_id):
        logger.info(f"GET - Histórico Retirada {retirada_id}")

        try:
            cacheKey = setCacheKey("historico", retirada_id)
            cache = verificarRedisCache("Historico de Retiradas", cacheKey)

            if cache:
                logger.info(f"Retornando Historico da Retirada {retirada_id} do Redis Cache")
                return json.loads(cache), 200

        except Exception:
            log_exception(f"Erro ao retornar o Historico da Retirada {retirada_id} do Redis Cache")
            abort(500, f"Erro ao retornar o Historico da Retirada {retirada_id} do Redis Cache")

        try:
            logger.info("Redis Cache vazio!")
            logger.info(f"Buscando o Historico da Retirada {retirada_id} no Banco de Dados")

            resultado = sqlRequisicaoGetById(retirada_id)

            preencherRedisCache(cacheKey, resultado)

            logger.info(f"Retornando o Historico da Retirada {retirada_id} do Banco de Dados")
            return resultado, 200

        except Exception:
            log_exception(f"Erro ao retornar o Historico da Retirada {retirada_id} do Banco de Dados")
            abort(500, f"Erro ao retornar o Historico da Retiradas {retirada_id} do Banco de Dados")
