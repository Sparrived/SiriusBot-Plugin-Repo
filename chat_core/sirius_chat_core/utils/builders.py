import inspect
import re
from types import FunctionType
from typing import Optional
from .message_chain import MessageChain

class FunctionBuilder:
    """函数工具"""
    def __init__(self, function: FunctionType, description: str):
        self.name = function.__name__
        self.description = description
        params = inspect.signature(function).parameters
        if not params:
            self.parameters = {}
            self.required_params = []
            return
        for name, param in params.items():
            if param.annotation is inspect.Parameter.empty:
                raise ValueError(f"参数 {name} 必须有类型注解")
        parameters = {name: param.annotation for name, param in params.items()}
        param_docs = self._get_param_docs(function)
        self.parameters = {name: {"type": annotation, "description": param_docs.get(name, "")} for name, annotation in parameters.items()}
        self.required_params = [name for name, param in params.items() if param.default is inspect.Parameter.empty]

    def build_function_json(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": self.parameters,
                "required": self.required_params
            }
        }

    def _get_param_docs(func: FunctionType) -> dict:
        doc = func.__doc__ or ""
        param_docs = {}
        # 匹配 Args: 块中的参数说明
        matches = re.findall(r'^\s*(\w+)\s*\(([^)]+)\):\s*(.+)$', doc, re.MULTILINE)
        for name, _, desc in matches:
            param_docs[name] = desc.strip()
        return param_docs
    
    @staticmethod
    def _foo(a: int, b: str):
        """
        Args:
            a (int): 第一个参数，整数类型
            b (str): 第二个参数，字符串类型
        """
        pass

class MessageChainBuilder:
    _messages: list[dict]
    def __init__(self):
        self._messages = []

    def create_new_message_chain(self, system_prompt: str):
        """构建消息链"""
        self._messages.append({"role": "system", "content": system_prompt})

    def add_user_message(self, content: str, img_base64: Optional[str] = None):
        """添加用户消息到消息链"""
        if self._messages is None:
            self._messages = []
        if len(self._messages) > 1 and self._messages[-1]["role"] == "user":
            raise ValueError("用户消息不能连续发送")
        if img_base64:
            self._messages.append({"role": "user",
                                    "content": [{"type": "image_url", 
                                         "image_url":{
                                             "url": f"data:image/jpeg;base64,{img_base64}",
                                             "detail":"low"
                                             }
                                        }, 
                                    {"type": "text", "text": content}]})
        else:
            self._messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str):
        """添加助手消息到消息链"""
        if self._messages is None:
            self._messages = []
        if len(self._messages) > 1 and self._messages[-1]["role"] == "assistant":
            raise ValueError("助手消息不能连续发送")
        self._messages.append({"role": "assistant", "content": content})
    
    def clear_message_chain(self):
        """清空消息链"""
        self._messages = []
    
    def build(self) -> MessageChain:
        """得到消息链字符串,并清空当前消息链"""
        if not self._messages:
            raise ValueError("消息链为空，请先添加消息")
        messages = self._messages
        self.clear_message_chain()
        return MessageChain(messages)