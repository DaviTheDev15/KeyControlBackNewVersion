from helpers.database import db

from models.Reserva import TB_Reserva
from models.ReservaDia import TB_ReservaDia


class ReservaRepository:

    @staticmethod
    def get_all(query):
        return db.session.execute(query).scalars().all()


    @staticmethod
    def get_by_id(reserva_id):
        return db.session.get(TB_Reserva, reserva_id)


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
    def delete(reserva):
        db.session.delete(reserva)
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