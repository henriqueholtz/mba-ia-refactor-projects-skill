from src.database.connection import get_db

STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


def _build_pedidos(rows, itens_rows):
    itens_by_pedido = {}
    for item in itens_rows:
        pid = item["pedido_id"]
        itens_by_pedido.setdefault(pid, []).append({
            "produto_id": item["produto_id"],
            "produto_nome": item["produto_nome"] or "Desconhecido",
            "quantidade": item["quantidade"],
            "preco_unitario": item["preco_unitario"],
        })

    result = []
    for row in rows:
        result.append({
            "id": row["id"],
            "usuario_id": row["usuario_id"],
            "status": row["status"],
            "total": row["total"],
            "criado_em": row["criado_em"],
            "itens": itens_by_pedido.get(row["id"], []),
        })
    return result


def _fetch_itens(db, pedido_ids):
    placeholders = ",".join("?" * len(pedido_ids))
    return db.execute(
        f"""
        SELECT i.pedido_id, i.produto_id, i.quantidade, i.preco_unitario,
               p.nome AS produto_nome
        FROM itens_pedido i
        LEFT JOIN produtos p ON p.id = i.produto_id
        WHERE i.pedido_id IN ({placeholders})
        """,
        pedido_ids,
    ).fetchall()


def get_pedidos_usuario(usuario_id):
    db = get_db()
    rows = db.execute(
        "SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,)
    ).fetchall()
    if not rows:
        return []
    itens = _fetch_itens(db, [r["id"] for r in rows])
    return _build_pedidos(rows, itens)


def get_todos():
    db = get_db()
    rows = db.execute("SELECT * FROM pedidos").fetchall()
    if not rows:
        return []
    itens = _fetch_itens(db, [r["id"] for r in rows])
    return _build_pedidos(rows, itens)


def criar(usuario_id, itens):
    db = get_db()

    total = 0
    for item in itens:
        produto = db.execute(
            "SELECT * FROM produtos WHERE id = ?", (item["produto_id"],)
        ).fetchone()
        if produto is None:
            return {"erro": f"Produto {item['produto_id']} não encontrado"}
        if produto["estoque"] < item["quantidade"]:
            return {"erro": f"Estoque insuficiente para {produto['nome']}"}
        total += produto["preco"] * item["quantidade"]

    cursor = db.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
        (usuario_id, total),
    )
    pedido_id = cursor.lastrowid

    for item in itens:
        produto = db.execute(
            "SELECT preco FROM produtos WHERE id = ?", (item["produto_id"],)
        ).fetchone()
        db.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
        )
        db.execute(
            "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
            (item["quantidade"], item["produto_id"]),
        )

    db.commit()
    return {"pedido_id": pedido_id, "total": total}


def atualizar_status(pedido_id, novo_status):
    db = get_db()
    db.execute(
        "UPDATE pedidos SET status = ? WHERE id = ?",
        (novo_status, pedido_id),
    )
    db.commit()
