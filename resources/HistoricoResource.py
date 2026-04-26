from flask_restful import Resource
from sqlalchemy import text
from flask import request, abort
from helpers.database import db
from helpers.logging import logger, log_exception
import json
from helpers.redis_cache import redis_client
from helpers.auxiliaryFunctionsResources.redisCacheFunctions import setCacheKey, verificarRedisCache, preencherRedisCache
from helpers.auxiliaryFunctionsResources.sqlRequestForHistory import sqlRequisicaoGetAll

class HistoricoResource(Resource):
    def get(self):
        logger.info("GET ALL - Histórico de Retiradas")

        try:
            cacheKey = f"historico:{json.dumps(request.args, sort_keys=True)}"
            
            cache = verificarRedisCache("historico", cacheKey)

            if cache:
                logger.info("Retornando Historico de Retiradas do Redis")
                return json.loads(cache), 200

        except Exception:
            log_exception("Erro ao retornar Historico de Retiradas do Redis Cache")
            abort(500, "Erro ao retornar Historico de Retiradas do Redis Cache")

        try:
            logger.info("Redis vazio!")
            logger.info("Buscando Retiradas no Banco de Dados")

            resultado = sqlRequisicaoGetAll()

            preencherRedisCache(cacheKey, resultado)

            logger.info("Retornando Retiradas do Banco de Dados")
            return resultado, 200

        except Exception:
            log_exception("Erro ao retornar Historico de Retiradas do Banco de Dados")
            abort(500, "Erro ao retornar Historico de Retiradas do Banco de Dados")


class HistoricoByIdResource(Resource):
    def get(self, retirada_id):
        logger.info(f"GET - Histórico Retirada {retirada_id}")

        try:
            cache_key = f"historico:{retirada_id}"
            cache = redis_client.get(cache_key)

            if cache:
                logger.info("Retornando histórico por ID do Redis")
                return json.loads(cache), 200

        except Exception:
            log_exception("Erro ao acessar Redis (Histórico by ID)")
            abort(500, "Erro ao acessar cache")

        try:
            logger.info("Buscando Retirada no Banco de Dados")

            sql = """
                SELECT
                    r.retirada_id,
                    r.data_retirada,
                    r.hora_retirada,
                    r.hora_prevista_devolucao,
                    r.hora_devolucao,
                    r.status,

                    s.sala_id,
                    s.sala_nome,

                    c.chave_id,
                    c.chave_nome,

                    resp.responsavel_id,
                    resp.responsavel_nome
                FROM tb_retirada r
                JOIN tb_chave c ON c.chave_id = r.chave_id
                JOIN tb_sala s ON s.sala_id = c.sala_id
                JOIN tb_responsavel resp ON resp.responsavel_id = r.responsavel_id
                WHERE r.status = 'devolvida'
                  AND r.retirada_id = :retirada_id
            """

            row = db.session.execute(
                text(sql),
                {"retirada_id": retirada_id}
            ).mappings().first()

            if not row:
                return {"erro": "Histórico não encontrado"}, 404

            resultado = dict(row)

            redis_client.setex(
                cache_key,
                10,
                json.dumps(resultado, default=str)
            )

            return resultado, 200

        except Exception:
            log_exception("Erro ao buscar histórico por ID")
            abort(500, "Erro ao buscar histórico")
