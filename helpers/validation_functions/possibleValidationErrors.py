erros_possiveis = {
    "required":"O campo {campo} é obrigatório.",

    "null":"O campo {campo} não pode ser nulo.",

    "validator_failed":"O campo {campo} deve ser valido (Maior que 0) e Corresponder a um {campo} existente.",

    "validate_positive":"O valor deve ser um número inteiro não negativo.",

    "invalid":"Formato inválido para {campo}.",

    "frequencia_data_fim":"Em uma reserva de {campo} única data_fim não pode ser diferente de data_inicio",

    "frequencia_semanal_quinzenal_dias_semana":"Em uma reserva de {campo} semanal ou quinzenal, o campo dias_semana não deve possuir uma lista vazia, [].",

    "data_inicio":"O campo {campo} não pode ser uma data passada.",

    "data_fim":"O campo {campo} deve ser maior ou igual há data_inicio.",

    "data_retirada":"O campo {campo} deve ser igual a data de hoje.",

    "hora_inicio":"O campo {campo} não pode ser um horário passado.",
    
    "hora_fim":"O campo {campo} deve ser maior que hora_inicio.",

    "hora_retirada":"O campo {campo} ultrapassa o limite de tolerância de 5 minutos.",

    "hora_prevista_devolucao":"O campo {campo} deve ser maior que hora_retirada.",

    "hora_devolucao":"O campo {campo} não pode ser anterior a hora_retirada.",

    "post_hora_devolucao":"O campo {campo} não pode ser informada no POST.",

    "not_hora_devolucao_devolvida":"O campo {campo} é obrigatória quando status é 'devolvida'.",

    "hora_devolucao_devolvida":"O campo {campo} só deve existir quando status é 'devolvida'.",

    "status":"No POST, o campo {campo} deve ser 'retirada.'"
    }