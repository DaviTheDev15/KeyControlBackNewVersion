from flask import request, abort
from flask_restful import Resource, marshal
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException
from helpers.logging import logger, log_exception
from models.Reserva import (
    TB_ReservaSchema,
    tb_reserva_fields
)
from repositories.reservaRepository import ReservaRepository
from services.reservaService import ReservaService


class TB_ReservasResource(Resource):

    def get(self):

        logger.info("GET ALL - Listagem de Reservas")

        try:

            resposta = ReservaService.listar()

            return resposta, 200

        except SQLAlchemyError:

            log_exception(
                "Erro SQLAlchemy ao buscar Reservas"
            )

            ReservaRepository.rollback()

            abort(
                500,
                description="Erro ao buscar Reservas no banco de dados."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao buscar Reservas"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )


    def post(self):

        logger.info("POST - Nova Reserva")

        schema = TB_ReservaSchema()

        dados = request.get_json()

        try:

            validado = schema.load(dados)

            resposta = ReservaService.criar(validado)

            if isinstance(resposta, tuple):
                return resposta

            return marshal(
                resposta,
                tb_reserva_fields
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
                "Erro SQLAlchemy ao criar Reserva"
            )

            ReservaRepository.rollback()

            abort(
                500,
                description="Erro ao criar Reserva."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao criar Reserva"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )


class TB_ReservaResource(Resource):

    def get(self, reserva_id):

        logger.info(
            f"GET - Reserva {reserva_id}"
        )

        try:

            resposta = ReservaService.buscar_por_id(
                reserva_id
            )

            return resposta, 200

        except SQLAlchemyError:

            log_exception(
                "Erro SQLAlchemy ao buscar Reserva"
            )

            abort(
                500,
                description="Erro ao buscar Reserva."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao buscar Reserva"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )


    def put(self, reserva_id):

        logger.info(
            f"PUT - Editando Reserva {reserva_id}"
        )

        schema = TB_ReservaSchema()

        dados = request.get_json()

        try:

            validado = schema.load(
                dados,
                partial=True
            )

            resposta = ReservaService.atualizar(
                reserva_id,
                validado
            )

            if isinstance(resposta, tuple):
                return resposta

            return marshal(
                resposta,
                tb_reserva_fields
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
                "Erro SQLAlchemy ao atualizar Reserva"
            )

            ReservaRepository.rollback()

            abort(
                500,
                description="Erro ao atualizar Reserva."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao atualizar Reserva"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )


    def delete(self, reserva_id):

        logger.info(
            f"DELETE - Reserva {reserva_id}"
        )

        try:

            ReservaService.remover(
                reserva_id
            )

            return {
                "mensagem": "Reserva removida com sucesso."
            }, 200

        except SQLAlchemyError:

            log_exception(
                "Erro SQLAlchemy ao remover Reserva"
            )

            ReservaRepository.rollback()

            abort(
                500,
                description="Erro ao remover Reserva."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao remover Reserva"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )