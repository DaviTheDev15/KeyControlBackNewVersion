from sqlalchemy import text
from helpers.database import db

def existe_conflito_reserva_raw(
    sala_id,
    hora_inicio,
    hora_fim,
    data_inicio,
    reserva_id_excluir=None
):
    dia_semana = data_inicio.weekday() + 1
    dia_mes = data_inicio.day

    sql = text("""
        SELECT 1
        FROM tb_reserva r
        LEFT JOIN tb_reserva_dia d ON d.reserva_id = r.reserva_id
        WHERE r.status = 'ativa'
          AND r.sala_id = :sala_id
          AND (:hora_inicio < r.hora_fim AND :hora_fim > r.hora_inicio)
          AND r.data_inicio <= :data_inicio
          AND (r.data_fim IS NULL OR r.data_fim >= :data_inicio)
          AND (
                -- 🔹 semanal
                (r.frequencia = 'semanal' AND d.dia_semana = :dia_semana)

                -- 🔹 mensal
                OR (r.frequencia = 'mensal' AND EXTRACT(DAY FROM r.data_inicio) = :dia_mes)

                -- 🔹 única
                OR (r.frequencia = 'única' AND r.data_inicio = :data_inicio)
          )
          AND (:reserva_id_excluir IS NULL OR r.reserva_id <> :reserva_id_excluir)
        LIMIT 1
    """)

    params = {
        "sala_id": sala_id,
        "hora_inicio": hora_inicio,
        "hora_fim": hora_fim,
        "data_inicio": data_inicio,
        "dia_semana": dia_semana,
        "dia_mes": dia_mes,
        "reserva_id_excluir": reserva_id_excluir
    }

    return db.session.execute(sql, params).fetchone() is not None

def merge_reserva(reserva, dados):
    return {
        "sala_id": dados.get("sala_id", reserva.sala_id),
        "responsavel_id": dados.get("responsavel_id", reserva.responsavel_id),
        "hora_inicio": dados.get("hora_inicio", reserva.hora_inicio),
        "hora_fim": dados.get("hora_fim", reserva.hora_fim),
        "data_inicio": dados.get("data_inicio", reserva.data_inicio),
        "data_fim": dados.get("data_fim", reserva.data_fim),
        "frequencia": dados.get("frequencia", reserva.frequencia),
        "status": dados.get("status", reserva.status),
    }