from sqlalchemy import select

from helpers.database import db
from models.Retirada import TB_Retirada
from models.Chave import TB_Chave


class RetiradaRepository:

    @staticmethod
    def get_all(query):
        return db.session.execute(query).scalars().all()

    @staticmethod
    def get_by_id(retirada_id):
        return db.session.get(TB_Retirada, retirada_id)

    @staticmethod
    def save(retirada):
        db.session.add(retirada)
        db.session.commit()
        return retirada

    @staticmethod
    def update():
        db.session.commit()

    @staticmethod
    def delete(retirada):
        db.session.delete(retirada)
        db.session.commit()

    @staticmethod
    def flush():
        db.session.flush()

    @staticmethod
    def rollback():
        db.session.rollback()

    @staticmethod
    def get_retirada_ativa_da_sala(sala_id):
        return (
            db.session.query(TB_Retirada)
            .join(TB_Chave, TB_Retirada.chave_id == TB_Chave.chave_id)
            .filter(
                TB_Chave.sala_id == sala_id,
                TB_Retirada.status.in_(["retirada", "atrasada"])
            )
            .first()
        )