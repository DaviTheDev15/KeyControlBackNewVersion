from flask_restful import Resource
from sqlalchemy import text
from flask import request, abort
from helpers.database import db
from helpers.logging import logger, log_exception
import json
from helpers.redis_cache import redis_client


class HistoricoResource(Resource):
    def get(self):
        logger.info("GET ALL - Histórico de Retiradas")

        try:
            cache_key = f"historico:{json.dumps(request.args, sort_keys=True)}"
            cache = redis_client.get(cache_key)

            logger.info("Verificando dados de Retiradas no Redis Cache")
            if cache:
                logger.info("Retornando histórico do Redis")
                return json.loads(cache), 200

        except Exception:
            log_exception("Erro ao acessar Redis (Histórico)")
            abort(500, "Erro ao acessar cache")

        try:
            logger.info("Redis vazio!")
            logger.info("Buscando Retiradas no Banco de Dados")

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
            """

            params = {}

            if request.args.get("sala_id"):
                sql += " AND s.sala_id = :sala_id"
                params["sala_id"] = request.args.get("sala_id")

            if request.args.get("responsavel_id"):
                sql += " AND resp.responsavel_id = :responsavel_id"
                params["responsavel_id"] = request.args.get("responsavel_id")

            if request.args.get("responsavel_nome"):
                sql += " AND LOWER(resp.responsavel_nome) LIKE :responsavel_nome"
                params["responsavel_nome"] = f"%{request.args.get('responsavel_nome').lower()}%"

            sql += " ORDER BY r.data_retirada DESC, r.hora_retirada DESC"

            resultado = db.session.execute(text(sql), params).mappings().all()

            resultado = [    {
        **dict(row),
        "data_retirada": row["data_retirada"].isoformat() if row["data_retirada"] else None,
        "hora_retirada": row["hora_retirada"].isoformat() if row["hora_retirada"] else None,
        "hora_prevista_devolucao": row["hora_prevista_devolucao"].isoformat() if row["hora_prevista_devolucao"] else None,
        "hora_devolucao": row["hora_devolucao"].isoformat() if row["hora_devolucao"] else None,
    }
    for row in resultado]

            redis_client.setex(
                cache_key,
                120,
                json.dumps(resultado, default=str)
            )

            logger.info("Retornando Retiradas do Banco de Dados")
            return resultado, 200

        except Exception:
            log_exception("Erro ao buscar histórico de retiradas")
            abort(500, "Erro ao buscar histórico")


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
                120,
                json.dumps(resultado, default=str)
            )

            return resultado, 200

        except Exception:
            log_exception("Erro ao buscar histórico por ID")
            abort(500, "Erro ao buscar histórico")
