"""OpenAI e transporte para provedores compatíveis com Chat Completions."""
from __future__ import annotations

import os
from threading import Lock

from ..contracts import RotuloVisita
from .cliente import RespostaInvalida, TimeoutLLM, Uso, validar_resposta


class ClienteChatCompletions:
    fonte = "llm"

    def __init__(self, modelo: str, *, chave_env: str, base_url: str, timeout_s: float = 30.0) -> None:
        chave = os.environ.get(chave_env)
        if not chave:
            raise RuntimeError(f"{chave_env} ausente (use LLM_PROVEDOR=offline para rodar sem chave)")

        import openai

        self._openai = openai
        headers = None
        if chave_env != "OPENAI_API_KEY":
            headers = {"OpenAI-Organization": openai.Omit(), "OpenAI-Project": openai.Omit()}
        self._cli = openai.OpenAI(api_key=chave, base_url=base_url, timeout=timeout_s,
                                  max_retries=0, default_headers=headers)
        self.modelo = modelo
        self.uso = Uso()
        self._lock_uso = Lock()

    def _opcoes(self) -> dict:
        return {}

    def rotular(self, prompt: str) -> RotuloVisita:
        try:
            r = self._cli.chat.completions.create(
                model=self.modelo, messages=[{"role": "user", "content": prompt}], **self._opcoes()
            )
        except self._openai.APIConnectionError as e:
            raise TimeoutLLM(type(e).__name__) from e
        except self._openai.APIStatusError as e:
            if e.status_code in (408, 429) or e.status_code >= 500:
                raise TimeoutLLM(f"HTTP {e.status_code}") from e
            raise

        with self._lock_uso:
            self.uso.chamadas += 1
            if r.usage is not None:
                self.uso.tokens_entrada += r.usage.prompt_tokens or 0
                self.uso.tokens_saida += r.usage.completion_tokens or 0

        texto = r.choices[0].message.content if r.choices else None
        if not texto:
            raise RespostaInvalida("resposta sem texto")
        return validar_resposta(texto)


class ClienteOpenAI(ClienteChatCompletions):
    provedor = "openai"

    def __init__(self, modelo: str, timeout_s: float = 30.0) -> None:
        super().__init__(modelo, chave_env="OPENAI_API_KEY", base_url="https://api.openai.com/v1",
                         timeout_s=timeout_s)

    def _opcoes(self) -> dict:
        return {"response_format": {"type": "json_object"}, "max_completion_tokens": 120, "store": False}
