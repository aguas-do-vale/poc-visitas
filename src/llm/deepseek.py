"""Rotulagem pela API da DeepSeek."""
from .openai import ClienteChatCompletions


class ClienteDeepSeek(ClienteChatCompletions):
    provedor = "deepseek"

    def __init__(self, modelo: str, timeout_s: float = 30.0) -> None:
        super().__init__(modelo, chave_env="DEEPSEEK_API_KEY", base_url="https://api.deepseek.com",
                         timeout_s=timeout_s)

    def _opcoes(self) -> dict:
        return {"response_format": {"type": "json_object"}, "max_tokens": 120,
                "extra_body": {"thinking": {"type": "disabled"}}}
