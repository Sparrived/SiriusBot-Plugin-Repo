import json
from types import FunctionType
from typing import TYPE_CHECKING, Callable, Optional
from openai.types.chat import ChatCompletion

class ModelPlatform:
    def __init__(self, api_url: str, authorization: str, chat_api: str = "chat/completions", img_api: str = "images/generations"):
        self._api_url = api_url
        self._authorization = authorization
        self._chat_model_api = api_url + chat_api
        self._img_model_api = api_url + img_api
        self.custom_extra_body: Optional[Callable] = None

    def _build_headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._authorization}",
            "Content-Type": "application/json"
        }

    def response(self, payload: dict, extra_body: Optional[dict] = None) -> dict:
        headers = self._build_headers()
        return self.send_request(payload, headers, extra_body)

    def send_request(self, payload: dict, headers: dict, extra_body: Optional[dict] = None, funcs: Optional[list[FunctionType]] = None) -> dict:
        """发送请求，如需requests实现，重写此函数"""
        return self.send_request_openai(payload, extra_body, funcs)

    def send_request_openai(self, payload: dict, extra_body: Optional[dict] = None, funcs: Optional[list[FunctionType]] = None) -> dict:
        """使用 OpenAI SDK 发送请求"""
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

        completion : ChatCompletion = self._client.chat.completions.create(**payload)
        return json.loads(completion.model_dump_json())
    
    def send_img_request(self, payload: dict, headers: dict) -> dict:
        """发送图片生成请求，子类需要实现该方法"""
        pass