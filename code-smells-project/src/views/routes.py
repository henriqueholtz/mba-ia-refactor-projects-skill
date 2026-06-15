from flask import Blueprint, request
from src.controllers import (
    produto_controller,
    usuario_controller,
    pedido_controller,
    relatorio_controller,
)

bp = Blueprint("api", __name__)


# --- Produtos ---

@bp.get("/produtos")
def listar_produtos():
    return produto_controller.listar()


@bp.get("/produtos/busca")
def buscar_produtos():
    return produto_controller.buscar_query(
        request.args.get("q", ""),
        request.args.get("categoria"),
        request.args.get("preco_min"),
        request.args.get("preco_max"),
    )


@bp.get("/produtos/<int:id>")
def buscar_produto(id):
    return produto_controller.buscar(id)


@bp.post("/produtos")
def criar_produto():
    return produto_controller.criar(request.get_json())


@bp.put("/produtos/<int:id>")
def atualizar_produto(id):
    return produto_controller.atualizar(id, request.get_json())


@bp.delete("/produtos/<int:id>")
def deletar_produto(id):
    return produto_controller.deletar(id)


# --- Usuários ---

@bp.get("/usuarios")
def listar_usuarios():
    return usuario_controller.listar()


@bp.get("/usuarios/<int:id>")
def buscar_usuario(id):
    return usuario_controller.buscar(id)


@bp.post("/usuarios")
def criar_usuario():
    return usuario_controller.criar(request.get_json())


@bp.post("/login")
def login():
    return usuario_controller.login(request.get_json())


# --- Pedidos ---

@bp.post("/pedidos")
def criar_pedido():
    return pedido_controller.criar(request.get_json())


@bp.get("/pedidos")
def listar_todos_pedidos():
    return pedido_controller.listar_todos()


@bp.get("/pedidos/usuario/<int:usuario_id>")
def listar_pedidos_usuario(usuario_id):
    return pedido_controller.listar_usuario(usuario_id)


@bp.put("/pedidos/<int:pedido_id>/status")
def atualizar_status_pedido(pedido_id):
    return pedido_controller.atualizar_status(pedido_id, request.get_json())


# --- Relatórios ---

@bp.get("/relatorios/vendas")
def relatorio_vendas():
    return relatorio_controller.vendas()
