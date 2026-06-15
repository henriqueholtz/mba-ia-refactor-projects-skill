import logging
from flask import jsonify
from src.models import pedido_model
from src.services import notification_service
from src.middlewares.error_handler import ValidationError

logger = logging.getLogger(__name__)


def criar(dados):
    if not dados:
        raise ValidationError("Dados inválidos")

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        raise ValidationError("usuario_id é obrigatório")
    if not itens:
        raise ValidationError("Pedido deve ter pelo menos 1 item")

    resultado = pedido_model.criar(usuario_id, itens)

    if "erro" in resultado:
        raise ValidationError(resultado["erro"])

    notification_service.pedido_criado(resultado["pedido_id"], usuario_id)

    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201


def listar_usuario(usuario_id):
    pedidos = pedido_model.get_pedidos_usuario(usuario_id)
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def listar_todos():
    pedidos = pedido_model.get_todos()
    return jsonify({"dados": pedidos, "sucesso": True}), 200


def atualizar_status(pedido_id, dados):
    if not dados:
        raise ValidationError("Dados inválidos")

    novo_status = dados.get("status", "")
    if novo_status not in pedido_model.STATUS_VALIDOS:
        raise ValidationError(f"Status inválido. Válidos: {pedido_model.STATUS_VALIDOS}")

    pedido_model.atualizar_status(pedido_id, novo_status)
    notification_service.status_atualizado(pedido_id, novo_status)

    return jsonify({"sucesso": True, "mensagem": "Status atualizado"}), 200
