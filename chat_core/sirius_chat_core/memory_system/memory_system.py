from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models import ChatModel

from ..willingness_system import MessageContext

from ..ego import TalkSystem

from ..utils import MessageUnit, MessageChain, MessageChainBuilder
from .history_memory import HistoryMemory
from .relationship import Relationship


class MemorySystem:
    def __init__(self, work_path: Path, talk_system: TalkSystem, chat_model: "ChatModel"):
        self.history_memory = HistoryMemory(work_path)
        self.relationship = Relationship(work_path)
        self._short_term_memory: dict[str, list[MessageUnit]] = {}  # 用于存放短期记忆，类型为dict：目标，MessageUnit
        self._long_term_memory: dict[str, list[str]] = {}   # 用于存放长期记忆，为LLM传出的对话总结
        self._talk_system = talk_system
        self._chat_model = chat_model
        # -------- 构建MemorySystem线程池 ---------
        self._memory_thread = ThreadPoolExecutor(max_workers=4, thread_name_prefix="MemorySystem")
        self._memory_thread.submit(self._run_memory_system)
        self._memory_thread.submit(self._run_self_talk_collect)

    def get_short_term_memory(self, target: str, count: int) -> list[MessageUnit]:
        if target not in self._short_term_memory:
            self._short_term_memory[target] = []
        if count <= 0:
            return []
        if len(self._short_term_memory[target]) <= count:
            return self._short_term_memory[target]
        return self._short_term_memory[target][-count:]
    
    def add_short_term_memory(self, target: str, message_unit: MessageUnit):
        if target not in self._short_term_memory:
            self._short_term_memory[target] = []
        # 如果上一条的qqid和当前的qqid相同，则合并消息
        if not len(self._short_term_memory[target]) > 1:
            self._short_term_memory[target].append(message_unit)
            return
        if self._short_term_memory[target][-1].user_id == message_unit.user_id:
            self._short_term_memory[target][-1].message += "\n" + message_unit.message
            self._short_term_memory[target][-1].time = message_unit.time
            self._short_term_memory[target][-1].user_card = message_unit.user_card
        else:
            self._short_term_memory[target].append(message_unit)
            

    def get_context_chain(self, target: str, count: int) -> MessageChain:
        message_chain_builder = MessageChainBuilder.from_message_chain(self._chat_model.create_initial_message_chain())
        story = self.get_short_term_memory(target, count)
        one_chain_messages = []
        for message in story:
            if message.user_id == -1:
                message_chain_builder.add_user_message("\n".join(one_chain_messages))
                one_chain_messages = []
                message_chain_builder.add_assistant_message(message.message)
            else:
                one_chain_messages.append(str(message))
        message_chain_builder.add_user_message("\n".join(one_chain_messages))
        return message_chain_builder.build()

    def _run_memory_system(self):
        while True:
            time.sleep(1)
            self._short_term_memory = {k: v for k, v in self._short_term_memory.items() if v}
    
    def _run_self_talk_collect(self):
        while True:
            cmc, reply = self._talk_system.output_queue.get()
            cmc: MessageContext
            target = "G"+cmc.source_id if cmc.source_id else "P"+cmc.user_id
            self.add_short_term_memory(target, MessageUnit("SELF", -1, reply, time.strftime("%Y年%m月%d日 %H:%M", time.localtime())))