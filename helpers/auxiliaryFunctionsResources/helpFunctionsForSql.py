from flask import request

def aplicar_ordenacao(query, campos, padrao):
    sort = request.args.get("sort", padrao)
    order = request.args.get("order", "asc")

    if order.lower() not in ("asc", "desc"):
        order = "asc"

    coluna = campos.get(sort, campos[padrao])

    if order == "desc":
        return query.order_by(coluna.desc())

    return query.order_by(coluna.asc())