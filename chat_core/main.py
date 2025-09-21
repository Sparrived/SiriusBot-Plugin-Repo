import json
import time
from .model_platform import *
from .models import *
from sirius_core import SiriusPlugin
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent

class ChatCore(SiriusPlugin):
    """Siriusbot 用于聊天的核心插件"""
    name = "SiriusBot-Plugin-ChatCore"
    version = "1.0.0"
    description = "提供聊天相关的核心功能"

    async def on_load(self):
        super().pre_initialize_plugin()

        # -------- 注册config --------
        self.register_config("platform", "SiliconFlow", "使用的模型平台名称")
        self.register_config("api_key", "your_api_key_here", "模型平台的API Key")
        self.register_config("model_selection", 
                             {"FilterModel": "Qwen/Qwen3-8B",
                              "ChatModel": "deepseek-ai/DeepSeek-V3.1"},
                             "各类模型的名称选择，键为模型类型，值为具体模型名称", dict
                             )
        self.register_config("water_group", True, "是则在没有/chat前缀时也有概率回复", bool) # 你这英语水平……


        # -------- 注册对接的api平台 --------
        try:
            match self.config.get("platform", ""):
                # TODO: 拓展更多平台
                case "SiliconFlow":
                    platform = SiliconFlow
                case "OpenAI":
                    platform = OpenAI
                case _:
                    self._log.warning("未指定有效的模型平台，使用默认平台SiliconFlow")
                    platform = SiliconFlow
            self._platform : ModelPlatform = platform(self.config.get("api_key", "your_api_key_here"))
        except Exception as e:
            self._log.error(f"注册API平台失败: {e}，插件将不再继续加载。！！注意，这意味着插件无法正常工作！！")
            return

        # -------- 构建模型 --------
        self._filter_model = FilterModel(self.config.get("model_selection", {})["FilterModel"], self._platform)
        if not self._filter_model:
            self._log.error("未找到合适的过滤模型，插件将不再继续加载。！！注意，这意味着插件无法正常工作！！")
            return

        self._chat_model = ChatModel(self.config.get("model_selection", {})["ChatModel"], self._platform)
        if not self._chat_model:
            self._log.error("未找到合适的聊天模型，插件将不再继续加载。！！注意，这意味着插件无法正常工作！！")
            return
    
        # ------- 注册指令 --------
    @command_registry.command("chat", description="和机器人对话，机器人一定会回复")
    async def cmd_chat(self, msg: BaseMessageEvent, current_text: str):
        # TODO: 这里需要实现与聊天模型的对接
        response = self._chat_model.response(self._chat_model.create_initial_message_chain(current_text))
        reply = json.loads(response["choices"][0]["message"]["content"])
        validate = self._filter_model.validate_check(reply)
        for item, validity in zip(reply.get("content", []), validate.get("verified", [])):
            if msg.is_group_msg():
                if not validity['can_output']:
                    self._log.info(f"过滤模型拒绝输出: {item}")
                    await self.api.post_group_msg(msg.group_id, f"!!过滤({validity.get('reason', '')})")
                else:
                    await self.api.post_group_msg(msg.group_id, item)
            else:
                if not validity['can_output']:
                    self._log.info(f"过滤模型拒绝输出: {item}")
                    await self.api.post_private_msg(msg.user_id, f"!!过滤({validity.get('reason', '')})")
                else:
                    await self.api.post_private_msg(msg.user_id, item)
            time.sleep(len(item) / 3)  # 模拟打字延迟
            
