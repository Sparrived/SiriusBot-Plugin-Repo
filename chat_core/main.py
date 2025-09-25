import asyncio
import base64
import random
import time

import requests


from .sirius_chat_core.models import *
from .sirius_chat_core.models.model_platform import *
from .sirius_chat_core.willingness_system import *
from sirius_core import SiriusPlugin
from ncatbot.plugin_system import command_registry, on_message
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils import status
from .utils import send_message, get_message_type
from .sirius_chat_core.ego import TalkSystem, MemoticonSystem

from typing import TypeVar

T = TypeVar("T", bound=BaseModel)

class ChatCore(SiriusPlugin):
    """Siriusbot 用于聊天的核心插件"""
    name = "SiriusBot-Plugin-ChatCore"
    version = "1.0.0"
    description = "提供聊天相关的核心功能"

    async def on_load(self):
        super().pre_initialize_plugin()

        # -------- 注册config --------
        self.register_config("platforms", 
                             {
                                "SiliconFlow" : "your_api_key_here",
                                "OpenAI" : "your_api_key_here",
                                "VolcengineArk" : "your_api_key_here"
                             }, "平台与API Key的映射关系，键为平台名称，值为对应的API Key", dict)
        self.register_config("model_selection", 
                             {
                                "FilterModel": {"SiliconFlow": "Qwen/Qwen3-30B-A3B"},
                                "ChatModel": {"VolcengineArk": "deepseek-v3-1-250821"},
                                "TranslateModel": {"SiliconFlow": "Qwen/Qwen3-32B"},
                                "MemoticonModel": {"SiliconFlow": "Pro/Qwen/Qwen2.5-VL-7B-Instruct"}
                            },
                             "各类模型的名称选择，键为模型类型，值为具体模型名称", dict
                             )
        self.register_config("filter_mode", True, "是否启用过滤模型，启用后会通过过滤模型判断ChatModel输出是否合规", bool)
        self.register_config("water_group", True, "在没有/chat前缀时也有概率回复", bool) # 你这英语水平……

        model_selection = self.config["model_selection"]

        # -------- 构建模型 --------
        def get_model_instance(model_dict: dict, model_class: type[T]) -> T:
            try:
                platform, name = next(iter(model_dict.items()))
                platform = PLATFORMNAMEMAP[platform](self.config["platforms"][platform])
                return model_class(name, platform)
            except Exception as e:
                raise ValueError(f"未找到合适的模型: {e}，插件将不再继续加载。！！注意，这意味着插件无法正常工作！！")
        try:
            self._filter_model = get_model_instance(model_selection["FilterModel"], FilterModel)
            self._chat_model = get_model_instance(model_selection["ChatModel"], ChatModel)
            self._translate_model = get_model_instance(model_selection["TranslateModel"], TranslateModel)
            self._memoticon_model = get_model_instance(model_selection["MemoticonModel"], MemoticonModel)
        except ValueError as e:
            self._log.error(f"模型加载失败: {e}")
            return
        
        # ------- 注册相关系统 --------
        self._memoticon_system = MemoticonSystem(self.workspace, self._memoticon_model)
        self._talk_system = TalkSystem(self._chat_model, self._memoticon_system)

        # -------- 注册意愿计算器相关processor --------
        # TODO: processor的开关
        w_calculator.register_processor(MentionProcessor())

    async def chat(self, msg: BaseMessageEvent, message_context: MessageContext):
        """构建消息链，把chat丢到对话系统"""
        mc = self._chat_model.create_initial_message_chain(message_context.message)
        if msg.is_group_msg():
            target = "G"+msg.group_id
        else:
            target = "P"+msg.user_id
        if message_context.message_type in [MessageType.AT, MessageType.TEXT, MessageType.REPLY]:
            msg = f"<message><user:{msg.sender.nickname}/><user_qqid:{msg.sender.user_id}/>{message_context.message}</message>"
            message_context.message = msg
        self._talk_system.create_talk(self._log, target, mc, message_context, send_message, self._filter_model if self.config["filter_mode"] else None)

    # ------- 注册指令 --------
    @command_registry.command("chat", description="和机器人对话，机器人一定会回复")
    async def cmd_chat(self, msg: BaseMessageEvent, current_text: str):
        """与机器人对话的指令"""
        mc = MessageContext(
            user_id=msg.user_id, 
            source_id=msg.group_id if msg.is_group_msg() else None,
            message=current_text,
            message_type=MessageType.TEXT,
            timestamp=int(time.time()),
            mentioned_bot=False
            )
        await self.chat(msg, mc)
    
    @on_message
    async def on_message(self, msg: BaseMessageEvent):
        """监听消息，根据意愿值决定是否回复"""
        if msg.is_group_msg():
            if not self.config.get("water_group", True):
                return
        
        # -------- 表情包判别逻辑 --------
        if msg.message.filter_image():
            img = msg.message.filter_image()[0]
            response = requests.get(img.url)
            response.raise_for_status()
            if random.random() <= 0.3:  # 30% 概率进行表情包注册逻辑
                try:
                    result = self._memoticon_system.judge_img(base64.b64encode(response.content).decode("utf-8"))
                    if result:
                        self._log.info(f"已注册表情包: {result}")
                except Exception as e:
                    self._log.error(f"表情包判别失败: {e}")
            return

        # -------- 回复逻辑 --------
        mentioned_bot = False
        message_type = MessageType.TEXT
        message = ""
        # 构建意愿值计算参数
        for segment in msg.message.messages:
            if get_message_type(segment) == "at":
                if segment.qq != msg.self_id:
                    continue
                # 能@的肯定是群消息，所以不用判断是否为群消息
                message += f"@{status.global_api.get_group_member_info_sync(msg.group_id, segment.qq).nickname} "
                message_type = MessageType.AT
            if get_message_type(segment) == "text":
                message += segment.text
                mentioned_bot = self._chat_model.is_mentioned(message)
                
        mc = MessageContext(
            user_id=msg.user_id, 
            source_id=msg.group_id if msg.is_group_msg() else None,
            message=message,
            message_type=message_type,
            timestamp=int(time.time()),
            mentioned_bot=mentioned_bot
            )
        
        result = await w_calculator.calculate_async(mc)
        self._log.debug(f"意愿值计算结果: {result}")
        if result["should_reply"]:
            await self.chat(msg, mc)



    async def on_unload(self):
        self._talk_system.dispose()
        # -------- 翻译模型 --------
        # if msg.raw_message.startswith("[CQ"):
        #     return
        # if msg.raw_message.startswith("/chat"):
        #     return
        # if len(msg.raw_message) < 3:
        #     return
        # response = self._translate_model.response(self._translate_model.create_initial_message_chain(msg.raw_message))
        # reply = json.loads(response["choices"][0]["message"]["content"])
        # if not reply.get("need_translate", False):
        #     return  # 不需要翻译，直接返回
        # translated = reply.get("translated", {})
        # if not translated:
        #     self._log.warning("翻译模型返回need_translate为True，但translated为空")
        #     return
        # source_content = translated.get("source_content", "")
        # target_content = translated.get("target_content", "")
        # self._log.info(f"翻译模型将内容翻译为中文，原文: {source_content}，译文: {target_content}")
        # if msg.is_group_msg():
        #     await self.api.post_group_msg(msg.group_id, f"检测到非中文语言，已翻译：\n原文: {source_content}，\n译文: {target_content}")
        # else:
        #     await self.api.post_private_msg(msg.user_id, f"检测到非中文语言，已翻译：\n原文: {source_content}，\n译文: {target_content}")