"""Cliente Azure Document Intelligence; nenhuma credencial é armazenada no código."""
import os
from io import BytesIO


def format_bounding_box(polygon):
    if not polygon:
        return None
    # O SDK pode fornecer pontos como objetos ou uma sequência de floats.
    if hasattr(polygon[0], "x"):
        return [[float(point.x), float(point.y)] for point in polygon]
    points = [float(v) for v in polygon]
    return [[points[i], points[i + 1]] for i in range(0, len(points) - 1, 2)]


def analyze_document(content: bytes):
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT", "").strip()
    key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY", "").strip()
    if not (endpoint.startswith("https://") and key):
        raise RuntimeError("Azure Document Intelligence não configurado.")

    from azure.ai.documentintelligence import DocumentIntelligenceClient
    from azure.core.credentials import AzureKeyCredential

    client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    poller = client.begin_analyze_document("prebuilt-read", body=BytesIO(content))
    result = poller.result()
    response = {"success": True, "demo": False, "content": result.content or "", "pages": [], "styles": []}
    for page in result.pages or []:
        info = {"page_number": page.page_number, "width": page.width, "height": page.height,
                "unit": page.unit, "lines": [], "words": []}
        for line in page.lines or []:
            info["lines"].append({"content": line.content, "bounding_box": format_bounding_box(line.polygon)})
        for word in page.words or []:
            info["words"].append({"content": word.content, "confidence": word.confidence,
                                  "bounding_box": format_bounding_box(word.polygon)})
        response["pages"].append(info)
    for style in result.styles or []:
        response["styles"].append({"is_handwritten": style.is_handwritten,
                                   "confidence": getattr(style, "confidence", None)})
    return response
