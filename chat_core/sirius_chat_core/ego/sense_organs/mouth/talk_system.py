import asyncio
import random
import threading
import time
from typing import TYPE_CHECKING, Callable, Optional
from queue import Queue

from ....utils.message_chain import MessageChain

from ....models import FilterModel

from ....willingness_system import MessageContext

from .memoticon_system import MemoticonSystem

if TYPE_CHECKING:
    from ....models import ChatModel

class TalkSystem:
    """聊天系统，解决模型高并发问题"""
    # AI 说不能用线程池代替这里的实现，可能需要考虑如何限制thread的数量。
    def __init__(self, model: "ChatModel", memoticon_system: MemoticonSystem):
        self._threads = {}  # target: {"thread": thread, "last_active": timestamp, "queue": []}
        self._lock = threading.Lock()
        self._reply_queue = Queue()
        self._model = model
        self._memoticon_system = memoticon_system
        self.output_queue = Queue()

    # FIXME: 这里的逻辑其实是有问题的，高并发应该减少调用次数，把多个内容合并到一个prompt后再发送，这样比较合理，并且模型可以更好的知道上下文
    # 暂时不想改了，等记忆系统搓出来再说吧
    def create_talk(self, log, target, message_chain: MessageChain, current_message_context: MessageContext, send_func: Callable, filter_model: Optional[FilterModel] = None):
        try:
            if self._mouth:
                pass
        except:
            self._mouth = threading.Thread(name="mouth", target=self._mouth_worker, args=(log, self._model._generate_reply_func, send_func), daemon=True)
            self._mouth.start()
        with self._lock:
            if target not in self._threads or not self._threads[target]["thread"].is_alive():
                # 新建线程
                queue = []
                t = threading.Thread(name=f"{target}_mouth",target=self._talk_worker, args=(target, queue), daemon=True)
                self._threads[target] = {"thread": t, "last_active": time.time(), "queue": queue}
                t.start()
            # 加入消息队列
            self._threads[target]["queue"].append((message_chain, current_message_context, filter_model))
            self._threads[target]["last_active"] = time.time()

    def _talk_worker(self, target, queue: list):
        while True:
            if queue:
                result = queue.pop(0)
                mc: MessageChain = result[0]
                cmc: MessageContext = result[1]
                filter = result[2]
                processed_data, validation_data, emotion = self._model._process_func(mc, filter)
                self._reply_queue.put((processed_data, validation_data, cmc, emotion))
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
            (processed_data, validation_data, cmc, emotion) = self._reply_queue.get()
            cmc: MessageContext
            for reply, origin_msg in generate_func(processed_data, validation_data):
                if origin_msg:
                    log.info(f"过滤模型认为 {origin_msg} 不应输出，因为 {reply[6:]}")
                if cmc.source_id:
                    log.info(f"发送消息到群组 {cmc.source_id}: {reply}，机器人目前心情: {emotion}")
                    self.output_queue.put((cmc, reply))
                    asyncio.run(send_func("group", cmc.source_id, reply))
                    
                else:
                    log.info(f"发送消息到私聊 {cmc.user_id}: {reply}，机器人目前心情: {emotion}")
                    self.output_queue.put((cmc, reply))
                    asyncio.run(send_func("private", cmc.user_id, reply))
                    
            if cmc.source_id:
                self.send_meme(log, send_func, "group", cmc.source_id, emotion)
            else:
                self.send_meme(log, send_func, "private", cmc.user_id, emotion)

    def send_meme(self, log, send_func: Callable, target, target_id, emotion: str = "平静"):
        img_path = self._memoticon_system.get_image(emotion)
        if not img_path:
            return
        if random.random() <= 0.7:
            log.info(f"发送表情包到 {target} {target_id}: {img_path}")
            asyncio.run(send_func(target, target_id, image=img_path))

    def dispose(self):
        with self._lock:
            self._threads.clear()
            self._mouth = None
