import logging
import re
from flask import jsonify
from src.models import usuario_model
from src.middlewares.error_handler import ValidationError

logger = logging.getLogger(__name__)

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def listar():
    usuarios = usuario_model.get_todos()
    return jsonify({"dados": usuarios, "sucesso": True}), 200


def buscar(id):
    usuario = usuario_model.get_por_id(id)
    if not usuario:
        raise ValidationError("Usuário não encontrado", 404)
    return jsonify({"dados": usuario, "sucesso": True}), 200


def criar(dados):
    if not dados:
        raise ValidationError("Dados inválidos")

    nome = dados.get("nome", "").strip()
    email = dados.get("email", "").strip()
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    if not _EMAIL_RE.match(email):
        raise ValidationError("Formato de email inválido")

    id = usuario_model.criar(nome, email, senha)
    logger.info("Usuário criado: %s", email)
    return jsonify({"dados": {"id": id}, "sucesso": True}), 201


def login(dados):
    if not dados:
        raise ValidationError("Dados inválidos")

    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not email or not senha:
        raise ValidationError("Email e senha são obrigatórios")

    usuario = usuario_model.login(email, senha)
    if usuario:
        logger.info("Login bem-sucedido: %s", email)
        return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200

    logger.warning("Login falhou: %s", email)
    raise ValidationError("Email ou senha inválidos", 401)
