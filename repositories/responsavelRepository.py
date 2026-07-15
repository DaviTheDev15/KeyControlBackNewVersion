from helpers.database import db
from helpers.auxiliaryFunctionsResources.helpFunctionsForSql import aplicar_ordenacao

from models.Responsavel import TB_Responsavel


class ResponsavelRepository:

    @staticmethod
    def get_all(query):

        query = db.select(TB_Responsavel)

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
        return db.session.get(TB_Responsavel, responsavel_id)


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
    def delete(responsavel: TB_Responsavel):
        db.session.delete(responsavel)
        db.session.commit()


    @staticmethod
    def rollback():
        db.session.rollback()