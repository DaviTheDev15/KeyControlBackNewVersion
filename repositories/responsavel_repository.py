from helpers.database import db
from helpers.auxiliaryFunctionsResources.helpFunctionsForSql import aplicar_ordenacao

from models.TB_Responsavel import TB_Responsavel


class ResponsavelRepository:

    @staticmethod
    def get_all():
        """
        Retorna todos os responsáveis aplicando a ordenação padrão.
        """

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
        """
        Busca um responsável pelo ID.
        """
        return db.session.get(TB_Responsavel, responsavel_id)


    @staticmethod
    def first():
        """
        Retorna o primeiro responsável cadastrado.
        """
        return db.session.query(TB_Responsavel).first()


    @staticmethod
    def save(responsavel: TB_Responsavel):
        """
        Salva um novo responsável.
        """
        db.session.add(responsavel)
        db.session.commit()

        return responsavel


    @staticmethod
    def update():
        """
        Persiste alterações realizadas em um responsável.
        """
        db.session.commit()


    @staticmethod
    def delete(responsavel: TB_Responsavel):
        """
        Remove um responsável.
        """
        db.session.delete(responsavel)
        db.session.commit()


    @staticmethod
    def rollback():
        """
        Desfaz a transação atual.
        """
        db.session.rollback()