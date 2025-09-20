from sirius_core import SiriusPlugin

class ChatCore(SiriusPlugin):
    """Siribot 用于聊天的核心插件"""
    name = "SiriusBot-Plugin-ChatCore"
    version = "1.0.0"
    description = "提供聊天相关的核心功能"

    async def on_load(self):
        super().pre_initialize_plugin()


