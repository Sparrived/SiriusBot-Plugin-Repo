from typing import override
from ncatbot.utils import get_log
from ncatbot.plugin_system import NcatBotPlugin
from .i18n_mixin import I18nMixin
from .api import SiriusCoreAPI

class SiriusPlugin(NcatBotPlugin, I18nMixin):
    """所有 SiriusBot 插件的基类，提供基础的国际化支持。**编写插件时请务必调在on_load()时候使用 super().on_load() 以确保正确初始化。**"""
    author = "Sparrived"
    dependencies = {"SiriusCore" : ">=1.0.0"}
    def __init__(self, *args, **kwargs) :
        self._log = get_log("UnknowSiriusPlugin")
        NcatBotPlugin.__init__(self, *args, **kwargs)

    def add_author(self, author_name : str) -> None:
        """"添加作者信息(但是应该没有人会和你一起开发啊喂？！)"""
        self.author += f", {author_name}"

    def loading(self) -> None:
        """插件加载时的初始化操作，任何子类在加载时应调用 super().loading() 以确保一些默认的初始化逻辑得以执行。"""
        self._log.name = self.name
        if self.name != "SiriusCore":
            while not SiriusCoreAPI.complete:
                # 等待SiriusCoreAPI初始化完成
                continue
        # ---- 注册config ----
        self.register_config("i18n", "zh-CN", "文本输出映射。")
        
        I18nMixin.__init__(self, self.workspace / "i18n", self.config["i18n"])
        