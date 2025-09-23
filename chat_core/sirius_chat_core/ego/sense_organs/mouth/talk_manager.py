import asyncio
import threading
import time
from typing import TYPE_CHECKING, Callable, Optional
from queue import Queue

from ....models import FilterModel

from ....willingness_system import MessageContext

if TYPE_CHECKING:
    from ....models import ChatModel

class TalkManager:
    """对话管理器，解决模型高并发问题"""
    # AI 说不能用线程池代替这里的实现，可能需要考虑如何限制thread的数量。
    def __init__(self):
        self._threads = {}  # target: {"thread": thread, "last_active": timestamp, "queue": []}
        self._lock = threading.Lock()
        self._reply_queue = Queue()

    # FIXME: 这里的逻辑其实是有问题的，高并发应该减少调用次数，把多个内容合并到一个prompt后再发送，这样比较合理，并且模型可以更好的知道上下文
    # 暂时不想改了，等记忆系统搓出来再说吧
    def create_talk(self, log, target, message_context: MessageContext, send_func: Callable, chat_model: "ChatModel", filter_model: Optional[FilterModel] = None):
        try:
            if self._mouth:
                pass
        except:
            self._mouth = threading.Thread(name="mouth", target=self._mouth_worker, args=(log, chat_model._generate_reply_func, send_func), daemon=True)
            self._mouth.start()
        with self._lock:
            if target not in self._threads or not self._threads[target]["thread"].is_alive():
                # 新建线程
                queue = []
                t = threading.Thread(name=f"{target}_mouth",target=self._talk_worker, args=(target, queue), daemon=True)
                self._threads[target] = {"thread": t, "last_active": time.time(), "queue": queue, "process_func": chat_model._process_func}
                t.start()
            # 加入消息队列
            self._threads[target]["queue"].append((message_context, filter_model))
            self._threads[target]["last_active"] = time.time()

    def _talk_worker(self, target, queue: list):
        while True:
            if queue:
                result = queue.pop(0)
                mc: MessageContext = result[0]
                filter = result[1]
                func = self._threads[target]["process_func"]
                processed_data, validation_data = func(mc, filter)
                self._reply_queue.put((processed_data, validation_data, mc))
                self._threads[target]["last_active"] = time.time()
            else:
                # 没有消息，检查是否超时
                if time.time() - self._threads[target]["last_active"] > 300:  # 5分钟
                    with self._lock:
                        del self._threads[target]
                    break
                time.sleep(1)

    def _mouth_worker(self, log, generate_func: Callable, send_func: Callable):
        while True:
            (processed_data, validation_data, message_context) = self._reply_queue.get()
            message_context: MessageContext
            for reply, origin_msg in generate_func(processed_data, validation_data):
                if origin_msg:
                    log.info(f"过滤模型认为 {origin_msg} 不应输出，因为 {reply[6:]}")
                if message_context.source_id:
                    asyncio.run(send_func("group", message_context.source_id, reply))
                else:
                    asyncio.run(send_func("private", message_context.user_id, reply))

    def dispose(self):
        with self._lock:
            self._threads.clear()
            self._mouth = None

talk_manager = TalkManager()