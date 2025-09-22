from types import FunctionType
from typing import Optional, override

from .model_platform import ModelPlatform
from openai import OpenAI

class OpenAI(ModelPlatform):
    def __init__(self, authorization: str):
        super().__init__(api_url="https://api.openai.com/v1/", authorization=authorization, chat_api="chat/completions")
        self._client = OpenAI(api_key=authorization)

    @override
    def send_request(self, payload: dict, headers: dict, funcs: Optional[list[FunctionType]] = None) -> dict:
        return self.send_request_openai(payload, funcs)

