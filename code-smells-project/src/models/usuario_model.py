from werkzeug.security import generate_password_hash, check_password_hash
from src.database.connection import get_db


def _row_to_dict(row, include_senha=False):
    d = {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }
    if include_senha:
        d["senha_hash"] = row["senha"]
    return d


def get_todos():
    rows = get_db().execute("SELECT * FROM usuarios").fetchall()
    return [_row_to_dict(r) for r in rows]


def get_por_id(id):
    row = get_db().execute("SELECT * FROM usuarios WHERE id = ?", (id,)).fetchone()
    return _row_to_dict(row) if row else None


def criar(nome, email, senha, tipo="cliente"):
    db = get_db()
    senha_hash = generate_password_hash(senha)
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    db.commit()
    return cursor.lastrowid


def login(email, senha):
    row = get_db().execute(
        "SELECT * FROM usuarios WHERE email = ?", (email,)
    ).fetchone()
    if row and check_password_hash(row["senha"], senha):
        return _row_to_dict(row)
    return None
