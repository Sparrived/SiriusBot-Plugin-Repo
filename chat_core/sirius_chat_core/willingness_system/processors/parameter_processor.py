from ..message_context import MessageContext

class ParameterProcessor:
    """参数处理器基类"""

    def __init__(self, weight: float = 0.1):
        self._name = self.__class__.__name__
        self._weight = weight
    
    async def process(self, context: MessageContext) -> float:
        """处理参数并返回分值"""
        raise NotImplementedError