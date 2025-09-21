from types import FunctionType
from typing import TYPE_CHECKING, Optional, override

if TYPE_CHECKING:
    from models import BaseModel

class ModelPlatform:
    def __init__(self, api_url: str, authorization: str):
        self._api_url = api_url
        self._authorization = authorization
    def _build_llm_payload(self, model: "BaseModel", messages: list[dict]) -> dict:
        return {
            "model": model._model_name,
            "messages": messages,
            "max_tokens": model._max_tokens,
            "stop": model._stop,
            "temperature": model._temperature,
            "top_p": model._top_p,
            "frequency_penalty": model._frequency_penalty,
            "n": model._n,
            "enable_thinking": model._enable_thinking,
            "thinking_budget": model._thinking_budget,
            "response_format": {"type": model._response_format},
        }
    
    def _build_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._authorization}",
            "Content-Type": "application/json"
        }

    def response(self, model: "BaseModel", messages: list[dict]) -> dict:
        payload = self._build_llm_payload(model, messages)
        headers = self._build_headers()

        return self.send_request(payload, headers)

    @override
    def send_request(self, payload: dict, headers: dict, funcs: Optional[list[FunctionType]] = None) -> dict:
        # 不同平台应该覆写自己的发送请求的逻辑。
        pass