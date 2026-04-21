erros_possiveis = {
    "required":"O campo {campo} é obrigatório.",
    "null":"O campo {campo} não pode ser nulo.",
    "validator_failed":"O campo {campo} deve ser valido (Maior que 0) e Corresponder a um {campo} existente.",
    "invalid":"Formato inválido para {campo}."
    }

def montarMensagemDeErro(nomeDoCampo, listaDeTiposDeErros, tipoInvalid=None):
    resposta = {}

    for erro in listaDeTiposDeErros:
        if erro in erros_possiveis:
            mensagem = erros_possiveis[erro].format(campo=nomeDoCampo)

            if tipoInvalid:
                if tipoInvalid == "b":
                    mensagem += f" Use apenas valores booleanos False ou True."

            resposta[erro] = mensagem

    return resposta