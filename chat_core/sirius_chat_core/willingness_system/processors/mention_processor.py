from typing import override

from .parameter_processor import ParameterProcessor
from ..message_context import MessageContext, MessageType


class MentionProcessor(ParameterProcessor):
    """提及参数处理器"""
    def __init__(self, weight: float = 0.6):
        super().__init__(weight)
    
    @override
    async def process(self, context: MessageContext) -> float:
        try:
            if context.message_type in [MessageType.AT, MessageType.REPLY]:
                return 1.0
            if context.mentioned_bot:
                return self._weight
        except:
            pass
        return 0.0