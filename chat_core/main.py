import asyncio
import json
import time

from .sirius_chat_core.models import *
from .sirius_chat_core.models.model_platform import *
from sirius_core import SiriusPlugin
from ncatbot.plugin_system import command_registry, on_message
from ncatbot.core.event import BaseMessageEvent


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
                                "TranslateModel": {"SiliconFlow": "Qwen/Qwen3-32B"}
                            },
                             "各类模型的名称选择，键为模型类型，值为具体模型名称", dict
                             )
        self.register_config("filter_mode", True, "是否启用过滤模型，启用后会通过过滤模型判断ChatModel输出是否合规", bool)
        self.register_config("water_group", True, "是则在没有/chat前缀时也有概率回复", bool) # 你这英语水平……

        model_selection = self.config["model_selection"]

        # -------- 构建模型 --------
        def get_model_instance(model_dict: dict, model_class: BaseModel) -> BaseModel:
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
        except ValueError as e:
            self._log.error(f"模型加载失败: {e}")
            return

    # ------- 注册指令 --------
    @command_registry.command("chat", description="和机器人对话，机器人一定会回复")
    async def cmd_chat(self, msg: BaseMessageEvent, current_text: str):
        """与机器人对话的指令"""
        processed_data = self._chat_model.get_process_data(self._chat_model.create_initial_message_chain(current_text))
        if self.config.get("filter_mode", True):
            validation_data = self._filter_model.get_process_data(self._filter_model.create_initial_message_chain(str(processed_data)))
            for verification_result, original_content in zip(validation_data["verified"], processed_data["content"]):
                can_output = verification_result.get("can_output", False)
                reason = verification_result.get("reason", "")
                if msg.is_group_msg():
                    if not can_output:
                        self._log.info(f"过滤模型认为 {original_content} 不应输出，因为 {reason}")
                        await self.api.post_group_msg(msg.group_id, f"!!过滤!!({reason})")
                    else:
                        await self.api.post_group_msg(msg.group_id, original_content)
                else:
                    if not can_output:
                        self._log.info(f"过滤模型认为 {original_content} 不应输出，因为 {reason}")
                        await self.api.post_private_msg(msg.user_id, f"!!过滤!!({reason})")
                    else:
                        await self.api.post_private_msg(msg.user_id, original_content)
                await asyncio.sleep(len(original_content) / 3)  # 模拟打字延迟
        else:
            for reply_msg in processed_data.get("content", []):
                if msg.is_group_msg():
                    await self.api.post_group_msg(msg.group_id, reply_msg)
                else:
                    await self.api.post_private_msg(msg.user_id, reply_msg)
                await asyncio.sleep(len(reply_msg) / 3)  # 模拟打字延迟

    @on_message
    async def on_message(self, msg: BaseMessageEvent):
        if not self.config.get("water_group", True):
            return
        
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