from helpers.redis_cache import redis_client
from helpers.logging import logger, log_exception
from flask import request, abort
import json

def setCacheKey(valor, adicional=None):
    cacheKey = ""
    if adicional:
        return cacheKey == f"{valor}:{adicional}"
    else:
        return cacheKey == f"{valor}:*"

def verificarRedisCache(nomeDoCampo,cacheKey):
    try:
        cache = redis_client.get(cacheKey)
        logger.info(f"Verificando dados de {nomeDoCampo} no Redis Cache")
        if cache:
            return cache
        
    except Exception:
        log_exception(f"Erro ao acessar Redis de{nomeDoCampo}")
        abort(500, f"Erro ao acessar Redis Cache de {nomeDoCampo}")

def preencherRedisCache(cacheKey, resultado):
    redis_client.setex(
            cacheKey,
            10,
            json.dumps(resultado, default=str)
        )

    