"""OCR: upload de imagem com processamento real no Azure ou demo sinalizada."""
from io import BytesIO
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from PIL import Image, UnidentifiedImageError
from services.document_intelligence import analyze_document

load_dotenv()
LOG = logging.getLogger(__name__)
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_UPLOAD_MB", "4")) * 1024 * 1024
EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tiff", "tif"}
VALID_FORMATS = {"PNG", "JPEG", "BMP", "TIFF"}


def demo_result():
    """Conteúdo fictício e fixo apenas para demonstrar a interface."""
    text = "DOCUMENTO DEMONSTRATIVO AI-901\nTeste de reconhecimento de texto\nExemplo sem processamento Azure"
    lines = [
        {"content": "DOCUMENTO DEMONSTRATIVO AI-901", "bounding_box": [[25, 30], [550, 30], [550, 80], [25, 80]]},
        {"content": "Teste de reconhecimento de texto", "bounding_box": [[25, 90], [480, 90], [480, 130], [25, 130]]},
        {"content": "Exemplo sem processamento Azure", "bounding_box": [[25, 150], [500, 150], [500, 190], [25, 190]]},
    ]
    words = [{"content": word, "confidence": 0.99, "bounding_box": [[0, 0], [0, 0], [0, 0], [0, 0]]}
             for word in text.split()]
    return {"success": True, "demo": True,
            "notice": "SIMULAÇÃO LOCAL: os textos são exemplos fixos; o arquivo enviado não foi submetido a OCR.",
            "content": text, "pages": [{"page_number": 1, "width": 620, "height": 260, "unit": "pixel",
                                        "lines": lines, "words": words}], "styles": []}


@app.get("/")
def index():
    return render_template("index.html", demo_mode=os.getenv("APP_MODE", "demo").lower() != "azure")


@app.post("/api/analyze")
def analyze():
    uploaded = request.files.get("image")
    if not uploaded or not uploaded.filename:
        return jsonify({"success": False, "error": "Selecione uma imagem."}), 400
    extension = Path(uploaded.filename).suffix.lower().lstrip(".")
    if extension not in EXTENSIONS:
        return jsonify({"success": False, "error": "Formato não suportado."}), 415
    content = uploaded.read()
    if not content:
        return jsonify({"success": False, "error": "Arquivo vazio."}), 400
    try:
        with Image.open(BytesIO(content)) as img:
            img.verify()
            if img.format not in VALID_FORMATS:
                raise UnidentifiedImageError()
    except (UnidentifiedImageError, ValueError, OSError):
        return jsonify({"success": False, "error": "O conteúdo enviado não é uma imagem válida."}), 415

    if os.getenv("APP_MODE", "demo").lower() != "azure":
        return jsonify(demo_result())
    try:
        return jsonify(analyze_document(content))
    except RuntimeError as exc:
        return jsonify({"success": False, "error": str(exc)}), 503
    except Exception:
        LOG.exception("Falha no Document Intelligence")
        return jsonify({"success": False, "error": "Falha ao analisar a imagem no serviço Azure."}), 502


@app.errorhandler(413)
def too_large(_error):
    return jsonify({"success": False, "error": "Arquivo ultrapassa o limite configurado."}), 413


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5001")), debug=False)
