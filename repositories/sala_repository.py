from helpers.database import db
from helpers.auxiliaryFunctionsResources.helpFunctionsForSql import aplicar_ordenacao
from models.TB_Sala import TB_Sala
from models.TB_Chave import TB_Chave

class SalaRepository:
    
    @staticmethod
    def get_all(query):
        query = db.select(TB_Sala)

        query = aplicar_ordenacao(query,{
            "id":TB_Sala.sala_id,
            "nome":TB_Sala.sala_nome,
            "disponivel":TB_Sala.disponivel
        }, "id"
        )

        return db.session.execute(query).scalars().all()
    

    @staticmethod
    def get_by_id(sala_id: int):
        return db.session.get(TB_Sala, sala_id)
    

    @staticmethod
    def first():
        return db.session.query(TB_Sala).first()
    

    @staticmethod
    def save(sala: TB_Sala):
        db.session.add(sala)
        db.session.commit()

        return sala
    

    @staticmethod
    def update():
        db.session.commit()


    @staticmethod
    def get_chaves_da_sala(sala_id):
        return (
            db.session.query(TB_Chave)
            .filter(TB_Chave.sala_id == sala_id)
            .order_by(TB_Chave.chave_id)
            .all()
        )


    @staticmethod
    def delete(sala: TB_Sala):
        db.session.delete(sala)
        db.session.commit()


    @staticmethod
    def rollback():
        db.session.rollback()
        

    @staticmethod
    def save_chave(chave):
        db.session.add(chave)
        db.session.commit()

        return chave