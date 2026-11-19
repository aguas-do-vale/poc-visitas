"""Rotulagem pela API do OpenCode Console."""
from __future__ import annotations

from .openai import ClienteChatCompletions


class ClienteOpenCode(ClienteChatCompletions):
    provedor = "opencode"

    def __init__(self, modelo: str, timeout_s: float = 30.0) -> None:
        super().__init__(modelo, chave_env="OPENCODE_API_KEY",
                         base_url="https://opencode.ai/inference/openai/v1", timeout_s=timeout_s)

    def _opcoes(self) -> dict:
        # O suporte ao formato JSON varia com o modelo; a rotulagem valida o texto.
        return {"max_tokens": 512}
