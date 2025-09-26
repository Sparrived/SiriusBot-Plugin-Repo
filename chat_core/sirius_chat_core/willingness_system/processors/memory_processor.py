from typing import override

from ...memory_system.memory_system import MemorySystem

from .parameter_processor import ParameterProcessor
from ..message_context import MessageContext, MessageType


class MemoryProcessor(ParameterProcessor):
    """记忆参数处理器"""
    def __init__(self,memory_system: MemorySystem, weight: float = 0.6):
        super().__init__(weight)
        self._memory_system = memory_system

    @override
    async def process(self, context: MessageContext) -> float:
        memory = self._memory_system.get_short_term_memory(context.source_id, 5)
        if not memory:
            return 0.0
        # TODO: 这样太简单了，实际上应该判断历史记忆和传入内容的相关度来输出，先这么用着吧
        return min(self._weight * 0.2 * len(memory), self._weight)