from flask import request, abort
from flask_restful import Resource, marshal
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from helpers.logging import logger, log_exception

from models.Sala import (
    TB_SalaSchema,
    tb_sala_fields
)

from repositories.salaRepository import SalaRepository
from services.salaService import SalaService


class TB_SalasResource(Resource):

    def get(self):

        logger.info("GET ALL - Listagem de Salas")

        text = request.args.get("q", "*")

        try:

            resposta = SalaService.listar(text)

            return resposta, 200

        except SQLAlchemyError:

            log_exception("Erro SQLAlchemy ao buscar Salas")

            SalaRepository.rollback()

            abort(
                500,
                description="Erro ao buscar Salas."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception("Erro inesperado ao buscar Salas")

            abort(
                500,
                description="Erro interno inesperado."
            )


    def post(self):

        logger.info("POST - Nova Sala")

        schema = TB_SalaSchema()

        dados = request.get_json()

        try:

            validado = schema.load(dados)

            sala = SalaService.criar(validado)

            return marshal(
                sala,
                tb_sala_fields
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
                "Erro SQLAlchemy ao inserir Sala"
            )

            SalaRepository.rollback()

            abort(
                500,
                description="Erro ao inserir Sala."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao inserir Sala"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )


class TB_SalaResource(Resource):

    def get(self, sala_id):

        logger.info(
            f"GET BY ID - Sala {sala_id}"
        )

        try:

            resposta = SalaService.buscar_por_id(
                sala_id
            )

            return resposta, 200

        except SQLAlchemyError:

            log_exception(
                "Erro SQLAlchemy ao buscar Sala"
            )

            abort(
                500,
                description="Erro ao buscar Sala."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao buscar Sala"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )


    def put(self, sala_id):

        logger.info(
            f"PUT - Editando Sala {sala_id}"
        )

        schema = TB_SalaSchema()

        dados = request.get_json()

        try:

            atualizados = schema.load(
                dados,
                partial=True
            )

            sala = SalaService.atualizar(
                sala_id,
                atualizados
            )

            return marshal(
                sala,
                tb_sala_fields
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
                "Erro SQLAlchemy ao atualizar Sala"
            )

            SalaRepository.rollback()

            abort(
                500,
                description="Erro ao atualizar Sala."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao atualizar Sala"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )


    def delete(self, sala_id):

        logger.info(
            f"DELETE - Sala {sala_id}"
        )

        try:

            SalaService.remover(
                sala_id
            )

            return {
                "mensagem": "Sala removida com sucesso."
            }, 200

        except SQLAlchemyError:

            log_exception(
                "Erro SQLAlchemy ao remover Sala"
            )

            SalaRepository.rollback()

            abort(
                500,
                description="Erro ao remover Sala."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao remover Sala"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )