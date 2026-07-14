from flask import request, abort
from flask_restful import Resource, marshal
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from helpers.logging import logger, log_exception

from models.TB_Chave import (
    TB_ChaveSchema,
    tb_chave_fields
)

from repositories.chave_repository import ChaveRepository
from services.chaves_service import ChaveService


class TB_ChavesResource(Resource):

    def get(self):

        logger.info("GET ALL - Listagem de Chaves")

        try:

            resposta = ChaveService.listar()

            return resposta, 200

        except SQLAlchemyError:

            log_exception(
                "Erro SQLAlchemy ao buscar Chaves"
            )

            ChaveRepository.rollback()

            abort(
                500,
                description="Erro ao buscar Chaves no banco de dados."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao buscar Chaves"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )


    def post(self):

        logger.info("POST - Nova Chave")

        schema = TB_ChaveSchema()

        dados = request.get_json()

        try:

            validado = schema.load(dados)

            chave = ChaveService.criar(
                validado
            )

            return marshal(
                chave,
                tb_chave_fields
            ), 201

        except ValidationError as err:

            logger.info(
                f"Dados inválidos: {err.messages}"
            )

            return {
                "erro": "Dados inválidos",
                "detalhes": err.messages
            }, 422

        except SQLAlchemyError:

            log_exception(
                "Erro SQLAlchemy ao inserir Chave"
            )

            ChaveRepository.rollback()

            abort(
                500,
                description="Erro ao inserir Chave."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao inserir Chave"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )


class TB_ChaveResource(Resource):

    def get(self, chave_id):

        logger.info(
            f"GET BY ID - Chave {chave_id}"
        )

        try:

            resposta = ChaveService.buscar_por_id(
                chave_id
            )

            return resposta, 200

        except SQLAlchemyError:

            log_exception(
                "Erro SQLAlchemy ao buscar Chave"
            )

            abort(
                500,
                description="Erro ao buscar Chave."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao buscar Chave"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )


    def put(self, chave_id):

        logger.info(
            f"PUT - Editando Chave {chave_id}"
        )

        schema = TB_ChaveSchema()

        dados = request.get_json()

        try:

            atualizados = schema.load(
                dados,
                partial=True
            )

            chave = ChaveService.atualizar(
                chave_id,
                atualizados
            )

            return marshal(
                chave,
                tb_chave_fields
            ), 200

        except ValidationError as err:

            logger.info(
                f"Dados inválidos: {err.messages}"
            )

            return {
                "erro": "Dados inválidos",
                "detalhes": err.messages
            }, 422

        except SQLAlchemyError:

            log_exception(
                "Erro SQLAlchemy ao atualizar Chave"
            )

            ChaveRepository.rollback()

            abort(
                500,
                description="Erro ao atualizar Chave."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao atualizar Chave"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )


    def delete(self, chave_id):

        logger.info(
            f"DELETE - Apagando Chave {chave_id}"
        )

        try:

            resposta = ChaveService.remover(
                chave_id
            )

            if resposta is not None:
                return resposta

            return {
                "mensagem": "Chave removida com sucesso"
            }, 200

        except SQLAlchemyError:

            log_exception(
                "Erro SQLAlchemy ao remover Chave"
            )

            ChaveRepository.rollback()

            abort(
                500,
                description="Erro ao remover Chave."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao remover Chave"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )