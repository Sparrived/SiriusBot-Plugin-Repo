from types import FunctionType
from typing import Optional

from .model_platform import ModelPlatform
from openai import OpenAI
from openai.types.chat import ChatCompletion

import json

class SiliconFlow(ModelPlatform):
    def __init__(self, authorization: str):
        super().__init__(api_url="https://api.siliconflow.cn/v1/chat/completions", authorization=authorization)
        self._client = OpenAI(api_key=authorization, base_url="https://api.siliconflow.cn/v1")

    def send_request(self, payload: dict, headers: dict, funcs: Optional[list[FunctionType]] = None) -> dict:
        extra_body = {"thinking": payload.pop("enable_thinking", False), "thinking_budget": payload.pop("thinking_budget", 512)}
        completion : ChatCompletion = self._client.chat.completions.create(**payload, extra_body=extra_body)

        # 处理 API 返回的所有工具调用请求
        if not completion.choices[0].message.tool_calls:
            return json.loads(completion.model_dump_json())
        
        for tool_call in completion.choices[0].message.tool_calls:
            func_name = tool_call.function.name
            func_args = tool_call.function.arguments
            if not funcs or func_name not in [f.__name__ for f in funcs]:
                raise ValueError(f"模型请求调用未注册的函数: {func_name}")
            func_out = next(f for f in funcs if f.__name__ == func_name)(**func_args)
            payload["messages"].append({
                "role": "tool",
                "content": func_out,
                "tool_call_id": tool_call.id
            })

        completion = self._client.chat.completions.create(**payload)
        return json.loads(completion.model_dump_json())

