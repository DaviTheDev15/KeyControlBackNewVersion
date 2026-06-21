from flask import request

def aplicar_ordenacao(query, campos, padrao):
    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc")

    if order.lower() not in ("asc", "desc"):
        order = "asc"

    coluna = campos.get(sort, campos[padrao])

    if order == "desc":
        return query.order_by(coluna.desc())

    return query.order_by(coluna.asc())


def aplicar_ordenacao_historico(sql):
    sort = request.args.get("sort", "data_retirada")
    order = request.args.get("order", "desc")

    campos = {
        "id": "r.retirada_id",
        "data": "r.data_retirada",
        "sala": "s.sala_nome",
        "responsavel": "resp.responsavel_nome",
        "chave": "c.chave_nome"
    }

    coluna = campos.get(sort, campos["data_retirada"])

    if order.lower() == "asc":
        sql += f" ORDER BY {coluna} ASC"
    else:
        sql += f" ORDER BY {coluna} DESC"

    return sql


def aplicar_filtros_historico(sql, params):
    if request.args.get("sala_id"):
        sql += " AND s.sala_id = :sala_id"
        params["sala_id"] = request.args.get("sala_id")

    if request.args.get("responsavel_id"):
        sql += " AND resp.responsavel_id = :responsavel_id"
        params["responsavel_id"] = request.args.get("responsavel_id")

    if request.args.get("responsavel_nome"):
        sql += " AND LOWER(resp.responsavel_nome) LIKE :responsavel_nome"
        params["responsavel_nome"] = f"%{request.args.get('responsavel_nome').lower()}%"

    return sql, params