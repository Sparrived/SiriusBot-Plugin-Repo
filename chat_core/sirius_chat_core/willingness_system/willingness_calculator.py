import asyncio
from typing import Any, Dict, List
from .processors.parameter_processor import ParameterProcessor
from .message_context import MessageContext

class WillingnessCalculator:
    """意愿值计算器"""
    def __init__(self, threshold: float = 0.667):
        self._threshold = threshold
        self._processors: List[ParameterProcessor] = []
        self._history: List[Dict[str, Any]] = []
    
    def register_processor(self, processor: ParameterProcessor) -> None:
        """注册参数处理器"""
        self._processors.append(processor)
    
    async def calculate_async(self, context: MessageContext) -> Dict[str, Any]:
        """异步计算意愿值"""
        total_score = 0.0
        details = {}

        # 并发调度processor
        tasks = [processor.process(context) for processor in self._processors]
        scores = await asyncio.gather(*tasks)

        for i, (processor, score) in enumerate(zip(self._processors, scores)):
            total_score += score
            details[f'processor_{i}'] = {
                'score': score,
                'type': processor.__class__.__name__
            }

        total_score = min(total_score, 1.0)
        result = {
            'total_score': total_score,
            'should_reply': total_score >= self._threshold,
            'details': details,
            'timestamp': context.timestamp
        }
        self._history.append(result)
        return result
    
    def calculate(self, context: MessageContext) -> Dict[str, Any]:
        """同步计算意愿值"""
        return asyncio.run(self.calculate_async(context))
    
    
    def set_threshold(self, threshold: float) -> None:
        """动态设置阈值"""
        self._threshold = threshold
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self._history:
            return {}
        
        scores = [entry['total_score'] for entry in self._history]
        reply_count = sum(1 for entry in self._history if entry['should_reply'])
        
        return {
            'total_messages': len(self._history),
            'reply_rate': reply_count / len(self._history),
            'avg_score': sum(scores) / len(scores),
            'max_score': max(scores),
            'min_score': min(scores)
        }

# 创建全局意愿值计算器
willingness_calculator = WillingnessCalculator()