import logging
from flask import Flask, jsonify
from flask_cors import CORS
from src.config import settings
from src.database.connection import init_app
from src.views.routes import bp
from src.middlewares import error_handler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG

    CORS(app)
    init_app(app)
    error_handler.register(app)
    app.register_blueprint(bp)

    @app.get("/")
    def index():
        return jsonify({
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "1.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        })

    @app.get("/health")
    def health_check():
        from src.database.connection import get_db
        db = get_db()
        produtos = db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
        usuarios = db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
        pedidos = db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
        return jsonify({
            "status": "ok",
            "database": "connected",
            "counts": {"produtos": produtos, "usuarios": usuarios, "pedidos": pedidos},
            "versao": "1.0.0",
        })

    return app


if __name__ == "__main__":
    app = create_app()
    logging.info("=" * 50)
    logging.info("SERVIDOR INICIADO — http://localhost:5000")
    logging.info("=" * 50)
    app.run(host="0.0.0.0", port=5000, debug=settings.DEBUG)
