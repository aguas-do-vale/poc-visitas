"""Rotulagem pela Gemini Developer API."""
from __future__ import annotations

import os
from threading import Lock

from ..contracts import RotuloVisita
from .cliente import TimeoutLLM, Uso, validar_resposta


class ClienteGemini:
    fonte = "llm"
    provedor = "gemini"

    def __init__(self, modelo: str, timeout_s: float = 30.0) -> None:
        chave = os.environ.get("GEMINI_API_KEY")
        if not chave:
            raise RuntimeError("GEMINI_API_KEY ausente (use LLM_PROVEDOR=offline para rodar sem chave)")
        from google import genai
        from google.genai import errors, types
        from httpx import TransportError

        self._cli = genai.Client(
            api_key=chave,
            vertexai=False,
            http_options=types.HttpOptions(timeout=int(timeout_s * 1000), retry_options=types.HttpRetryOptions(attempts=1)),
        )
        self._erro_api = errors.APIError
        self._erro_transporte = TransportError
        self._config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_json_schema=RotuloVisita.model_json_schema(),
        )
        self.modelo = modelo
        self.uso = Uso()
        self._lock = Lock()

    def rotular(self, prompt: str) -> RotuloVisita:
        try:
            resposta = self._cli.models.generate_content(model=self.modelo, contents=prompt, config=self._config)
        except self._erro_transporte as e:
            raise TimeoutLLM("Falha de conexão com Gemini") from e
        except self._erro_api as e:
            if e.code in (408, 429) or 500 <= e.code < 600:
                raise TimeoutLLM(f"Gemini HTTP {e.code}") from e
            raise
        with self._lock:
            self.uso.chamadas += 1
            if uso := resposta.usage_metadata:
                self.uso.tokens_entrada += uso.prompt_token_count or 0
                self.uso.tokens_saida += (uso.candidates_token_count or 0) + (uso.thoughts_token_count or 0)
        return validar_resposta(resposta.text or "")
