from types import FunctionType
from typing import TypeVar, override
from typing_extensions import deprecated
from ..utils import *
from .model_platform import ModelPlatform

T = TypeVar("Model", bound="BaseModel")

class BaseModel:
    def __init__(self, 
                 system_prompt: str, 
                 model_name: str,
                 platform : ModelPlatform,
                 temperature: float = 0.7,
                 top_p: float = 1.0,
                 top_k: int = 50,
                 max_tokens: int = 1024,
                 frequency_penalty: float = 0.0,
                 presence_penalty: float = 0.0,
                 enable_streaming: bool = False,
                 enable_thinking: bool = False,
                 thinking_budget: int = 512,
                 stop: list[str] = [],
                 n: int = 1,
                 response_format: str = "json_object"
                 ):
        self._system_prompt = system_prompt
        self._temperature = temperature
        self._top_p = top_p
        self._top_k = top_k
        self._max_tokens = max_tokens
        self._model_name = model_name
        self._frequency_penalty = frequency_penalty
        self._presence_penalty = presence_penalty
        self._enable_streaming = enable_streaming
        self._enable_thinking = enable_thinking
        self._thinking_budget = thinking_budget
        self._stop = stop
        self._tools : list[dict[str, str|dict]] = []
        self._n = n
        self._response_format = response_format
        self._platform = platform

    def create_initial_message_chain(self, user_message: str):
        mcb = MessageChainBuilder()
        mcb.create_new_message_chain(self._system_prompt)
        mcb.add_user_message(user_message)
        return mcb.build()

    def add_tool(self, func: FunctionType, desc: str = ""):
        try:
            self._tools.append({"type": "function", "function": FunctionBuilder(function=func, description=desc).build_function_json()})
        except Exception as e:
            raise ValueError(f"构建工具失败: {e}")
    
    def _response(self, messages: MessageChain) -> dict:
        """发送请求并返回响应结果，得到全部响应结果的内容"""
        return self._platform.response(self, messages.messages)
    
    def _process_data(self, model_output: dict) -> dict:
        """处理响应结果，提取有用信息"""
        pass

    def get_process_data(self, messages: MessageChain) -> dict:
        """获取处理后的数据"""
        try:
            model_output = self._response(messages)
            return self._process_data(model_output)
        except Exception as e:
            raise ValueError(f"获取处理后的数据失败: {e}")
