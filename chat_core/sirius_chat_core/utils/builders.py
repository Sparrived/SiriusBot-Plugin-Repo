import inspect
import re
from types import FunctionType

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