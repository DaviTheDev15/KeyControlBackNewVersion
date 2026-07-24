from helpers.database import db
from helpers.auxiliaryFunctionsResources.helpFunctionsForSql import aplicar_ordenacao
from datetime import datetime, UTC
from models.Responsavel import TB_Responsavel
from sqlalchemy import select

class ResponsavelRepository:

    @staticmethod
    def get_all(query):

        query = (db.select(TB_Responsavel).where(TB_Responsavel.deleted_at.is_(None)))

        query = aplicar_ordenacao(
            query,
            {
                "id": TB_Responsavel.responsavel_id,
                "nome": TB_Responsavel.responsavel_nome,
                "ativo": TB_Responsavel.ativo
            },
            "id"
        )

        return db.session.execute(query).scalars().all()


    @staticmethod
    def get_by_id(responsavel_id: int):
        query = (
            db.select(TB_Responsavel)
            .where(
                TB_Responsavel.responsavel_id == responsavel_id,
                TB_Responsavel.deleted_at.is_(None)
            )
        )

        return db.session.execute(query).scalar_one_or_none()


    @staticmethod
    def first():
        return db.session.query(TB_Responsavel).first()


    @staticmethod
    def save(responsavel: TB_Responsavel):
        db.session.add(responsavel)
        db.session.commit()

        return responsavel


    @staticmethod
    def update():
        db.session.commit()


    @staticmethod
    def soft_delete(responsavel: TB_Responsavel, deleted_by:int):
        responsavel.deleted_at = datetime.now(UTC)
        responsavel.deleted_by = deleted_by
        db.session.commit()


    @staticmethod
    def rollback():
        db.session.rollback()