from helpers.database import db

from models.Chave import TB_Chave


class ChaveRepository:

    @staticmethod
    def get_all(query):
        return db.session.execute(query).scalars().all()


    @staticmethod
    def get_by_id(chave_id: int):
        return db.session.get(TB_Chave, chave_id)


    @staticmethod
    def save(chave: TB_Chave):
        db.session.add(chave)
        db.session.commit()

        return chave


    @staticmethod
    def update():
        db.session.commit()


    @staticmethod
    def delete(chave: TB_Chave):
        db.session.delete(chave)
        db.session.commit()


    @staticmethod
    def rollback():
        db.session.rollback()