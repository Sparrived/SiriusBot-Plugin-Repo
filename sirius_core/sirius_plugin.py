import time
from ncatbot.utils import get_log
from ncatbot.plugin_system import NcatBotPlugin
from .i18n_mixin import I18nMixin
from .api import SiriusCoreAPI

class SiriusPlugin(NcatBotPlugin, I18nMixin):
    """所有 SiriusBot 插件的基类，提供基础的国际化支持。**编写插件时请务必在on_load()或_init_()时使用 super().pre_initialize_plugin() 以确保正确初始化。**"""
    author = "Sparrived"
    dependencies = {"SiriusCore" : ">=1.0.0"}
    def __init__(self, *args, **kwargs) :
        self._log = get_log(self.name)
        NcatBotPlugin.__init__(self, *args, **kwargs)

    def add_author(self, author_name : str) -> None:
        """"添加作者信息(希望我有朝一日能调用到这个方法)"""
        self.author += f", {author_name}"

    def pre_initialize_plugin(self) -> None:
        """插件加载时的初始化操作，任何子类在on_load或_init_时应调用 super().pre_initialize_plugin() 以确保一些默认的初始化逻辑得以执行。"""
        if self.name != "SiriusCore":
            while not SiriusCoreAPI.complete:
                # 等待SiriusCoreAPI初始化完成
                time.sleep(0.5)
        
        # ---- 初始化I18n ----
        self._log.debug(f"初始化 {self.name} 的i18n模块。")
        self.register_config("i18n", "zh-CN", "文本输出映射。")
        I18nMixin.__init__(self, self.workspace / "i18n", self.config["i18n"])

    async def on_reload(self) ->None:
        """插件重载时的操作"""
        self._log.info(f"插件 {self.name} 重载中...")
        # 重新加载i18n
        self.lang = self.config.get("i18n", "zh-CN")
        self._translations = self._load_translations()
        self._log.info(f"插件 {self.name} 重载完成。")