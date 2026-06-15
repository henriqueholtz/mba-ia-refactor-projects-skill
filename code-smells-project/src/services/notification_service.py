import logging

logger = logging.getLogger(__name__)


def pedido_criado(pedido_id, usuario_id):
    logger.info("NOTIFY email: Pedido %s criado para usuario %s", pedido_id, usuario_id)
    logger.info("NOTIFY sms: Seu pedido foi recebido!")
    logger.info("NOTIFY push: Novo pedido recebido pelo sistema")


def status_atualizado(pedido_id, novo_status):
    if novo_status == "aprovado":
        logger.info("NOTIFY: Pedido %s aprovado — preparar envio.", pedido_id)
    elif novo_status == "cancelado":
        logger.info("NOTIFY: Pedido %s cancelado — devolver estoque.", pedido_id)
