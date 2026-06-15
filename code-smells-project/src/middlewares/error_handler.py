import logging
from flask import jsonify

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    def __init__(self, message, status=400):
        super().__init__(message)
        self.status = status


def register(app):
    @app.errorhandler(ValidationError)
    def handle_validation(err):
        return jsonify({"erro": str(err), "sucesso": False}), err.status

    @app.errorhandler(404)
    def handle_404(err):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(Exception)
    def handle_generic(err):
        logger.exception("Unhandled error: %s", err)
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
