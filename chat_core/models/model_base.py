from types import FunctionType
from utils import *
from model_platform import ModelPlatform

class ModelBase:
    def __init__(self, system_prompt: str, 
                 temperature: float,
                 top_p: float, 
                 top_k: int, 
                 max_tokens: int, 
                 model_name: str,
                 frequency_penalty: float,
                 platform : ModelPlatform,
                 enable_streaming: bool = False,
                 enable_thinking: bool = False,
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
        self._enable_streaming = enable_streaming
        self._enable_thinking = enable_thinking
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
    
    def response(self, messages: MessageChain) -> dict:
        return self._platform.response(self, messages.messages)
