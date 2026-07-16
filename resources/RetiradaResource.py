from flask import request, abort
from flask_restful import Resource, marshal
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from helpers.logging import logger, log_exception

from models.Retirada import (
    TB_RetiradaSchema,
    tb_retirada_fields
)

from repositories.retiradaRepository import RetiradaRepository
from services.retiradaService import RetiradaService


class TB_RetiradasResource(Resource):

    def get(self):

        logger.info("GET ALL - Listagem de Retiradas")

        try:

            resposta = RetiradaService.listar()

            return resposta, 200

        except SQLAlchemyError:

            log_exception(
                "Erro SQLAlchemy ao buscar Retiradas"
            )

            RetiradaRepository.rollback()

            abort(
                500,
                description="Erro ao buscar Retiradas no banco de dados."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao buscar Retiradas"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )


    def post(self):

        logger.info("POST - Nova Retirada")

        schema = TB_RetiradaSchema()

        dados = request.get_json()

        try:

            validado = schema.load(dados)

            resposta = RetiradaService.criar(validado)

            if isinstance(resposta, tuple):
                return resposta

            return marshal(
                resposta,
                tb_retirada_fields
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
                "Erro SQLAlchemy ao criar Retirada"
            )

            RetiradaRepository.rollback()

            abort(
                500,
                description="Erro ao criar Retirada."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao criar Retirada"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )


class TB_RetiradaResource(Resource):

    def get(self, retirada_id):

        logger.info(
            f"GET - Retirada {retirada_id}"
        )

        try:

            resposta = RetiradaService.buscar_por_id(
                retirada_id
            )

            return resposta, 200

        except SQLAlchemyError:

            log_exception(
                "Erro SQLAlchemy ao buscar Retirada"
            )

            abort(
                500,
                description="Erro ao buscar Retirada."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao buscar Retirada"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )


    def put(self, retirada_id):

        logger.info(
            f"PUT - Editando Retirada {retirada_id}"
        )

        schema = TB_RetiradaSchema()

        dados = request.get_json()

        try:

            validado = schema.load(
                dados,
                partial=True
            )

            resposta = RetiradaService.atualizar(
                retirada_id,
                validado
            )

            return marshal(
                resposta,
                tb_retirada_fields
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
                "Erro SQLAlchemy ao atualizar Retirada"
            )

            RetiradaRepository.rollback()

            abort(
                500,
                description="Erro ao atualizar Retirada."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao atualizar Retirada"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )


    def delete(self, retirada_id):

        logger.info(
            f"DELETE - Retirada {retirada_id}"
        )

        try:

            RetiradaService.remover(
                retirada_id
            )

            return {
                "mensagem": "Retirada removida com sucesso."
            }, 200

        except SQLAlchemyError:

            log_exception(
                "Erro SQLAlchemy ao remover Retirada"
            )

            RetiradaRepository.rollback()

            abort(
                500,
                description="Erro ao remover Retirada."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao remover Retirada"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )