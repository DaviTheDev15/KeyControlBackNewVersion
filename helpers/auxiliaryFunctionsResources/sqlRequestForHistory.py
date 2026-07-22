from helpers.redis_cache import redis_client
from helpers.logging import logger, log_exception
from flask import request, abort
from helpers.database import db
from sqlalchemy import text
from helpers.auxiliaryFunctionsResources.helpFunctionsForSql import aplicar_ordenacao_historico, aplicar_filtros_historico

def sqlRequisicaoGetAll():
    try:
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

        sql = aplicar_ordenacao_historico(sql)

        resultado = db.session.execute(text(sql), params).mappings().all()

        resultado = [
            {
                **dict(row),
                "data_retirada": row["data_retirada"].isoformat() if row["data_retirada"] else None,
                "hora_retirada": row["hora_retirada"].isoformat() if row["hora_retirada"] else None,
                "hora_prevista_devolucao": row["hora_prevista_devolucao"].isoformat() if row["hora_prevista_devolucao"] else None,
                "hora_devolucao": row["hora_devolucao"].isoformat() if row["hora_devolucao"] else None,
            }
        for row in resultado]

        return resultado

    except Exception:
        log_exception("Erro ao buscar Historico de Retiradas")
        abort(500, "Erro ao buscar Historico de Retiradas")

def sqlRequisicaoGetById(retirada_id):
    try:
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
            WHERE r.retirada_id = :retirada_id
            """

        row = db.session.execute(
            text(sql),
            {"retirada_id": retirada_id}
        ).mappings().first()

        if not row:
            return {"erro": "Histórico não encontrado"}, 404

        resultado = dict(row)

        if resultado.get("data_retirada"):
            resultado["data_retirada"] = resultado["data_retirada"].isoformat()

        if resultado.get("hora_retirada"):
            resultado["hora_retirada"] = resultado["hora_retirada"].strftime("%H:%M")

        if resultado.get("hora_prevista_devolucao"):
            resultado["hora_prevista_devolucao"] = resultado["hora_prevista_devolucao"].strftime("%H:%M")

        if resultado.get("hora_devolucao"):
            resultado["hora_devolucao"] = resultado["hora_devolucao"].strftime("%H:%M")

        return resultado

    except Exception:
        log_exception(f"Erro ao buscar histórico por ID")
        abort(500, "Erro ao buscar histórico")