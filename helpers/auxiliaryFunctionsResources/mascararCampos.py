def mascarar_campos(lista, campos):
    for item in lista:
        for campo in campos:
            valor = item.get(campo)

            if valor:
                valor = str(valor)
                item[campo] = "X" * (len(valor) - 2) + valor[-2:]

    return lista