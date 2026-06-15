import logging
from flask import jsonify
from src.models import produto_model
from src.middlewares.error_handler import ValidationError

logger = logging.getLogger(__name__)

NOME_MIN = 2
NOME_MAX = 200


def listar():
    produtos = produto_model.get_todos()
    logger.info("Listando %d produtos", len(produtos))
    return jsonify({"dados": produtos, "sucesso": True}), 200


def buscar(id):
    produto = produto_model.get_por_id(id)
    if not produto:
        raise ValidationError("Produto não encontrado", 404)
    return jsonify({"dados": produto, "sucesso": True}), 200


def criar(dados):
    if not dados:
        raise ValidationError("Dados inválidos")
    for campo in ("nome", "preco", "estoque"):
        if campo not in dados:
            raise ValidationError(f"{campo.capitalize()} é obrigatório")

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if len(nome) < NOME_MIN:
        raise ValidationError("Nome muito curto")
    if len(nome) > NOME_MAX:
        raise ValidationError("Nome muito longo")
    if categoria not in produto_model.VALID_CATEGORIAS:
        raise ValidationError(f"Categoria inválida. Válidas: {produto_model.VALID_CATEGORIAS}")

    id = produto_model.criar(nome, descricao, preco, estoque, categoria)
    logger.info("Produto criado com ID %s", id)
    return jsonify({"dados": {"id": id}, "sucesso": True, "mensagem": "Produto criado"}), 201


def atualizar(id, dados):
    if not produto_model.get_por_id(id):
        raise ValidationError("Produto não encontrado", 404)
    if not dados:
        raise ValidationError("Dados inválidos")
    for campo in ("nome", "preco", "estoque"):
        if campo not in dados:
            raise ValidationError(f"{campo.capitalize()} é obrigatório")

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", "geral")

    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")

    produto_model.atualizar(id, nome, descricao, preco, estoque, categoria)
    return jsonify({"sucesso": True, "mensagem": "Produto atualizado"}), 200


def deletar(id):
    if not produto_model.get_por_id(id):
        raise ValidationError("Produto não encontrado", 404)
    produto_model.deletar(id)
    logger.info("Produto %s deletado", id)
    return jsonify({"sucesso": True, "mensagem": "Produto deletado"}), 200


def buscar_query(termo, categoria, preco_min_str, preco_max_str):
    try:
        preco_min = float(preco_min_str) if preco_min_str else None
        preco_max = float(preco_max_str) if preco_max_str else None
    except ValueError:
        raise ValidationError("preco_min e preco_max devem ser números")

    resultados = produto_model.buscar(termo, categoria, preco_min, preco_max)
    return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True}), 200
