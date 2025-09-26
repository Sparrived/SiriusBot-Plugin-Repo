import random
from typing import override

from .parameter_processor import ParameterProcessor
from ..message_context import MessageContext


class RandomProcessor(ParameterProcessor):
    """随机化处理器"""
    def __init__(self, weight: float = 0.4):
        super().__init__(weight)
    
    @override
    async def process(self, context: MessageContext) -> float:
        return random.uniform(0, self._weight)