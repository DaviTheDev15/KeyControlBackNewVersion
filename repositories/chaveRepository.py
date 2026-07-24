from helpers.database import db

from models.Chave import TB_Chave
from sqlalchemy import select
from datetime import datetime, UTC

class ChaveRepository:

    @staticmethod
    def get_all(query):
        query = (db.select(TB_Chave).where(TB_Chave.deleted_at.is_(None)))
        return db.session.execute(query).scalars().all()


    @staticmethod
    def get_by_id(chave_id: int):
        query = (
            db.select(TB_Chave)
            .where(
                TB_Chave.chave_id == chave_id,
                TB_Chave.deleted_at.is_(None)
            )
        )
        return db.session.execute(query).scalar_one_or_none()


    @staticmethod
    def save(chave: TB_Chave):
        db.session.add(chave)
        db.session.commit()

        return chave


    @staticmethod
    def update():
        db.session.commit()


    @staticmethod
    def soft_delete(chave: TB_Chave, deleted_by:int):
        chave.deleted_at = datetime.now(UTC)
        chave.deleted_by = deleted_by
        db.session.commit()


    @staticmethod
    def rollback():
        db.session.rollback()