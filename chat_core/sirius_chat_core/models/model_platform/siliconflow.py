from types import FunctionType
from typing import Optional, override

from .model_platform import ModelPlatform
from openai import OpenAI


class SiliconFlow(ModelPlatform):
    def __init__(self, authorization: str):
        super().__init__(api_url="https://api.siliconflow.cn/v1/", authorization=authorization)
        self._client = OpenAI(api_key=authorization, base_url="https://api.siliconflow.cn/v1")