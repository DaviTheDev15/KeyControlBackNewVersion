def montarMensagemDeErro(nomeDoCampo, indicadorDoTipo):
    if indicadorDoTipo == 3:
        return {
            "required":f"O campo {nomeDoCampo}é obrigatório",
            "null":f"O campo {nomeDoCampo} não pode ser nulo",
            "validator_failed":f"O campo {nomeDoCampo} deve ser valido(Maior que 0) e Corresponder a uma sala existente."
        }
    elif indicadorDoTipo == 2:
        return {
            "required":f"O campo {nomeDoCampo} é obrigatório.",
            "invalid":f"O campo {nomeDoCampo} aceita apenas valores booleanos(False e True)."
        }
    else:
        return {"Erro":"Tipo Invalido"}