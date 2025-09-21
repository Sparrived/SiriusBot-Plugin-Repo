from types import FunctionType
from typing import Optional, override

from .model_platform import ModelPlatform
from openai import OpenAI

class VolcengineArk(ModelPlatform):
    def __init__(self, authorization: str):
        super().__init__(api_url="https://ark.cn-beijing.volces.com/api/v3/chat/completions", authorization=authorization)
        self._client = OpenAI(api_key=authorization, base_url="https://ark.cn-beijing.volces.com/api/v3")

    @override
    def _build_extra_body(self, model):
        return {"thinking": {"type" : "enabled" if model._enable_thinking else "disabled"}}

    @override
    def send_request(self, payload: dict, headers: dict, funcs: Optional[list[FunctionType]] = None) -> dict:
        return self.send_request_openai(payload, funcs)
