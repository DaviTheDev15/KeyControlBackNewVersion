from flask import request, abort
from flask_restful import Resource, marshal
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from helpers.logging import logger, log_exception

from models.TB_Responsavel import (
    TB_ResponsavelSchema,
    tb_responsavel_fields
)

from repositories.responsavel_repository import ResponsavelRepository
from services.responsavel_service import ResponsavelService



class TB_ResponsaveisResource(Resource):

    def get(self):
        logger.info("GET ALL - Listagem de Responsáveis")

        text = request.args.get("q", "*")

        try:
            resposta = ResponsavelService.listar(text)

            return resposta, 200

        except SQLAlchemyError:
            log_exception("Erro SQLAlchemy ao buscar Responsáveis")
            ResponsavelRepository.rollback()
            abort(
                500,
                description="Erro ao buscar responsáveis no banco de dados."
            )

        except HTTPException:
            raise

        except Exception:
            log_exception("Erro inesperado ao buscar Responsáveis")
            abort(
                500,
                description="Erro interno inesperado."
            )


    def post(self):

        logger.info("POST - Novo Responsável")

        schema = TB_ResponsavelSchema()

        dados = request.get_json()

        try:

            validado = schema.load(dados)

            responsavel = ResponsavelService.criar(validado)

            return marshal(
                responsavel,
                tb_responsavel_fields
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
                "Erro SQLAlchemy ao inserir Responsável"
            )

            ResponsavelRepository.rollback()

            abort(
                500,
                description="Erro ao inserir Responsável."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao inserir Responsável"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )


class TB_ResponsavelResource(Resource):

    def get(self, responsavel_id):

        logger.info(
            f"GET BY ID - Responsável {responsavel_id}"
        )

        try:

            resposta = ResponsavelService.buscar_por_id(
                responsavel_id
            )

            return resposta, 200

        except SQLAlchemyError:

            log_exception(
                "Erro SQLAlchemy ao buscar Responsável"
            )

            abort(
                500,
                description="Erro ao buscar Responsável."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao buscar Responsável"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )


    def put(self, responsavel_id):

        logger.info(
            f"PUT - Responsável {responsavel_id}"
        )

        schema = TB_ResponsavelSchema()

        dados = request.get_json()

        try:

            atualizados = schema.load(
                dados,
                partial=True
            )

            responsavel = ResponsavelService.atualizar(
                responsavel_id,
                atualizados
            )

            return marshal(
                responsavel,
                tb_responsavel_fields
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
                "Erro SQLAlchemy ao atualizar Responsável"
            )

            ResponsavelRepository.rollback()

            abort(
                500,
                description="Erro ao atualizar Responsável."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao atualizar Responsável"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )


    def delete(self, responsavel_id):

        logger.info(
            f"DELETE - Responsável {responsavel_id}"
        )

        try:

            ResponsavelService.remover(
                responsavel_id
            )

            return {
                "mensagem": "Responsável removido com sucesso."
            }, 200

        except SQLAlchemyError:

            log_exception(
                "Erro SQLAlchemy ao remover Responsável"
            )

            ResponsavelRepository.rollback()

            abort(
                500,
                description="Erro ao remover Responsável."
            )

        except HTTPException:
            raise

        except Exception:

            log_exception(
                "Erro inesperado ao remover Responsável"
            )

            abort(
                500,
                description="Erro interno inesperado."
            )
