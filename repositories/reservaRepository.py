from helpers.database import db

from models.Reserva import TB_Reserva
from models.ReservaDia import TB_ReservaDia
from sqlalchemy import select
from datetime import datetime, UTC


class ReservaRepository:

    @staticmethod
    def get_all(query):
        query = (db.select(TB_Reserva).where(TB_Reserva.deleted_at.is_(None)))
        return db.session.execute(query).scalars().all()


    @staticmethod
    def get_by_id(reserva_id):
        query = (
            db.select(TB_Reserva)
            .where(
                TB_Reserva.reserva_id == reserva_id,
                TB_Reserva.deleted_at.is_(None)
            )
        )
        return db.session.execute(query).scalar_one_or_none()


    @staticmethod
    def save(reserva):
        db.session.add(reserva)
        db.session.commit()

        return reserva


    @staticmethod
    def flush():
        db.session.flush()


    @staticmethod
    def update():
        db.session.commit()


    @staticmethod
    def soft_delete(reserva: TB_Reserva, deleted_by: int):
        reserva.deleted_at = datetime.now(UTC)
        reserva.deleted_by = deleted_by
        db.session.commit()


    @staticmethod
    def rollback():
        db.session.rollback()


    @staticmethod
    def limpar_dias_semana(reserva_id):
        db.session.query(TB_ReservaDia)\
            .filter_by(reserva_id=reserva_id)\
            .delete()


    @staticmethod
    def adicionar_dia(reserva_id, dia_semana):
        db.session.add(
            TB_ReservaDia(
                reserva_id=reserva_id,
                dia_semana=dia_semana
            )
        )