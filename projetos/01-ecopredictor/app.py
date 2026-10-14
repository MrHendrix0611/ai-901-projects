"""EcoPredictor: interface original do SENAI e integração opcional com Azure ML.

APP_MODE=demo (padrão): fórmula ilustrativa, NÃO é inferência de ML.
APP_MODE=azure: chamada autenticada ao endpoint real do Azure Machine Learning.
"""
import json
import logging
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
LOG = logging.getLogger(__name__)

COLUMNS = [
    "dia", "mes", "ano", "estacao", "feriado", "dia_semana", "dia_util",
    "situacao_climatica", "temperatura", "sensacao_termica", "umidade", "velocidade_vento",
]
INT_COLUMNS = set(COLUMNS[:8])
RANGES = {
    "dia": (1, 31), "mes": (1, 12), "ano": (2011, 2100), "estacao": (1, 4),
    "feriado": (0, 1), "dia_semana": (0, 6), "dia_util": (0, 1),
    "situacao_climatica": (1, 4), "temperatura": (0, 1.2),
    "sensacao_termica": (0, 1.2), "umidade": (0, 1), "velocidade_vento": (0, 1),
}


def parse_input(form):
    """Retorna apenas as 12 colunas do modelo na mesma ordem esperada."""
    vals = []
    for field in COLUMNS:
        raw = form.get(field)
        if raw is None:
            raise ValueError(f"Campo obrigatório ausente: {field}")
        try:
            num = float(raw)
            if field in INT_COLUMNS:
                if not num.is_integer():
                    raise ValueError()
                num = int(num)
        except (ValueError, OverflowError):
            raise ValueError(f"Número inválido no campo: {field}") from None
        low, high = RANGES[field]
        if not (low <= num <= high):
            raise ValueError(f"Valor fora da faixa permitida: {field}")
        vals.append(num)
    return vals


def demo_prediction(values):
    """Apenas exemplo de interface. Não representa o modelo treinado no Azure."""
    row = dict(zip(COLUMNS, values))
    base = 4400
    value = (
        base + 1250 * (row["temperatura"] - 0.5)
        - 1250 * row["umidade"] - 1700 * row["velocidade_vento"]
        - 460 * (row["situacao_climatica"] - 1)
        + (260 if row["dia_util"] else -210)
    )
    return round(max(0, value), 2)


def normalize_prediction(payload):
    """Extrai a previsão dos formatos mais comuns de resposta de endpoints Azure ML."""
    if isinstance(payload, (int, float)) and not isinstance(payload, bool):
        return float(payload)
    if isinstance(payload, list) and payload:
        return normalize_prediction(payload[0])
    if isinstance(payload, dict):
        for key in ("Results", "results", "predictions", "prediction", "output", "result", "output1"):
            if key in payload:
                return normalize_prediction(payload[key])
        for key in ("alugueis", "predicted_value", "forecast"):
            if key in payload:
                return normalize_prediction(payload[key])
    raise ValueError("Formato de previsão inesperado. Confira o contrato em Endpoints > Testar.")


def call_azure(values):
    endpoint = os.getenv("AZURE_ML_ENDPOINT", "").strip()
    key = os.getenv("AZURE_ML_KEY", "").strip()
    deployment = os.getenv("AZURE_ML_DEPLOYMENT", "").strip()
    if not (endpoint.startswith("https://") and key):
        raise RuntimeError("Integração Azure não configurada no servidor.")
    body = json.dumps({"input_data": {"columns": COLUMNS, "index": [0], "data": [values]}}).encode("utf-8")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}
    if deployment:
        headers["azureml-model-deployment"] = deployment
    req = Request(endpoint, data=body, headers=headers, method="POST")
    with urlopen(req, timeout=30) as response:  # TLS é verificado por padrão
        data = json.load(response)
    return normalize_prediction(data)


@app.get("/")
def index():
    return render_template("index.html", demo_mode=os.getenv("APP_MODE", "demo").lower() != "azure")


@app.post("/predict")
def predict():
    try:
        values = parse_input(request.form)
    except ValueError as exc:
        return jsonify({"error": "invalid_input", "message": str(exc)}), 400

    if os.getenv("APP_MODE", "demo").lower() != "azure":
        return jsonify({
            "Results": [demo_prediction(values)],
            "demo": True,
            "notice": "SIMULAÇÃO LOCAL: resultado ilustrativo, sem inferência de IA ou chamada ao Azure.",
        })

    try:
        prediction = call_azure(values)
    except RuntimeError as exc:
        return jsonify({"error": "not_configured", "message": str(exc)}), 503
    except HTTPError as exc:
        LOG.warning("Azure ML retornou status HTTP %s", exc.code)
        return jsonify({"error": "azure_ml_http_error", "message": "Falha no endpoint Azure ML.", "status_code": exc.code}), 502
    except (URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError):
        LOG.exception("Erro de integração com Azure ML")
        return jsonify({"error": "azure_ml_unavailable", "message": "Não foi possível obter a previsão. Confira o deployment e o formato da resposta."}), 502
    return jsonify({"Results": [prediction], "demo": False})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)
