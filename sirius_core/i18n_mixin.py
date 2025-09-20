import json
import os
import importlib
from typing import Iterable, LiteralString, Optional, final
from ncatbot.core import BaseMessageEvent
from ncatbot.core.api import BotAPI

class I18nMixin:
    """国际化混入类，用于加载和获取多语言资源(主要用于高度自定义)"""

    _translations : dict

    def __init__(self, resource_dir: str, lang : str = "zh-CN"):
        """初始化i18n"""
        self.lang = lang
        self.resource_dir = resource_dir
        self._translations = self._load_translations()
        # 防止后期调用写错，建议使用SendMessage封装好的输出方法进行输出
        self.message_sender : MessageSendHelper = MessageSendHelper(self)

        # 提取默认翻译，防止有人忘记写某些翻译
        module_name = self.__class__.__module__.rsplit(".", 1)[0] + ".i18n"
        try:
            DEFAULT_TRANSLATIONS = importlib.import_module(module_name).DEFAULT_TRANSLATIONS
        except:
            DEFAULT_TRANSLATIONS = {}
        for k, v in DEFAULT_TRANSLATIONS.items():
            k = f"{getattr(self, 'name', __class__.__name__)}.{k}"
            if k not in self._translations:
                self._translations[k] = v
        # 保存翻译
        os.makedirs(self.resource_dir, exist_ok=True)
        path = os.path.join(self.resource_dir, f"{self.lang}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._translations, f, ensure_ascii=False, indent=4)
        
    @final
    def _load_translations(self):
        """加载资源映射表"""
        path = os.path.join(self.resource_dir, f"{self.lang}.json")
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
        
    @final
    def _translate(self, key: str, args: Optional[Iterable[LiteralString]] = None) -> str:
        """翻译相关句式"""
        tag = f"{getattr(self, "name", __class__.__name__)}.{key}"
        text = self._translations.get(tag, tag)
        if not args:
            return text
        if isinstance(args, str):
            try:
                text = text.format(args)
            except Exception:
                pass  # 如果格式化失败则返回原文
        else:
            try:
                text = text.format(*args)
            except Exception:
                pass  # 如果格式化失败则返回原文
        return text
    
class MessageSendHelper:
    """发送消息的辅助类"""
    def __init__(self, i18n : "I18nMixin"):
        self._i18n = i18n

    def _translate(self, key: str, args: Iterable[LiteralString] | LiteralString | None = None) -> str:
        """翻译相关句式"""
        return self._i18n._translate(key, args)
    
    @final
    async def reply_by_message_event(self, msg: BaseMessageEvent, key: str, args: Iterable[LiteralString] | LiteralString | None = None, **kargs) -> None:
        """通过BaseMessageEvent回复文本信息。"""
        await msg.reply(text=self._translate(key, args), **kargs)

    @final
    def reply_by_message_event_sync(self, msg: BaseMessageEvent, key: str, args: Iterable[LiteralString] | LiteralString | None = None, **kargs) -> None:
        """通过BaseMessageEvent回复文本信息，同步版本。"""
        msg.reply_sync(text=self._translate(key, args), **kargs)

    @final
    async def post_group_message(self, api : BotAPI, group_id : str | int, key : str, args: Iterable[LiteralString] | LiteralString | None = None, **kwargs) -> None:
        """通过BotAPI发送群消息。"""
        await api.post_group_msg(group_id=group_id, text=self._translate(key, args), **kwargs)

    @final
    def post_group_message_sync(self, api : BotAPI, group_id : str | int, key : str, args: Iterable[LiteralString] | LiteralString | None = None, **kwargs) -> None:
        """通过BotAPI发送群消息，同步版本。"""
        api.post_group_msg_sync(group_id=group_id, text=self._translate(key, args), **kwargs)

    @final
    async def post_private_message(self, api : BotAPI, user_id : str | int, key : str, args: Iterable[LiteralString] | LiteralString | None = None, **kwargs) -> None:
        """通过BotAPI发送私聊消息。"""
        await api.post_private_msg(user_id=user_id, text=self._translate(key, args), **kwargs)

    @final
    def post_private_message_sync(self, api : BotAPI, user_id : str | int, key : str, args: Iterable[LiteralString] | LiteralString | None = None, **kwargs) -> None:
        """通过BotAPI发送私聊消息，同步版本。"""
        api.post_private_msg_sync(user_id=user_id, text=self._translate(key, args), **kwargs)