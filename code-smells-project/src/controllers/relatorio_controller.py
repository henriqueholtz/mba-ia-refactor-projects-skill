from flask import jsonify
from src.models import relatorio_model

DISCOUNT_TIERS = [(10_000, 0.10), (5_000, 0.05), (1_000, 0.02)]


def vendas():
    dados = relatorio_model.vendas()

    faturamento = dados["faturamento_bruto"]
    desconto = next(
        (faturamento * rate for limit, rate in DISCOUNT_TIERS if faturamento > limit),
        0,
    )

    relatorio = {
        **dados,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "ticket_medio": round(faturamento / dados["total_pedidos"], 2)
        if dados["total_pedidos"] > 0
        else 0,
    }
    return jsonify({"dados": relatorio, "sucesso": True}), 200
