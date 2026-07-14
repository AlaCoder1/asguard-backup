"""
Asguard Assistant — REST API
============================
Local-LLM assistant (Ollama qwen2.5:1.5b) with a rule-based fallback. Offline,
free. Two endpoints: a streaming one (live, ChatGPT-style) used by the widget,
and a non-streaming one kept for compatibility.
"""
import json

from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import AllowAny

from backend.backup import assistant


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def assistant_ask(request):
    data = request.data if isinstance(request.data, dict) else {}
    message = (data.get("message") or "").strip()
    try:
        result = assistant.answer(message)
    except Exception as exc:
        return JsonResponse(
            {"intent": "error", "reply": "Désolé, je n'ai pas pu traiter la demande.",
             "refs": [], "error": str(exc)}, status=200)
    return JsonResponse(result, status=200)


@csrf_exempt
def assistant_stream(request):
    """Stream the answer token-by-token (text/plain chunks). Plain Django view so
    the response isn't buffered by DRF; disables nginx buffering too."""
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)
    try:
        payload = json.loads((request.body or b"{}").decode("utf-8"))
    except Exception:
        payload = {}
    message = (payload.get("message") or "").strip()

    def gen():
        try:
            for chunk in assistant.stream_answer(message):
                yield chunk
        except Exception:
            yield "⚠️ Erreur de l'assistant."

    resp = StreamingHttpResponse(gen(), content_type="text/plain; charset=utf-8")
    resp["Cache-Control"] = "no-cache"
    resp["X-Accel-Buffering"] = "no"   # stop nginx from buffering the stream
    return resp
