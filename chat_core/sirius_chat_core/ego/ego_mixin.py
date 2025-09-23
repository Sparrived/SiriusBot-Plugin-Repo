from typing import Optional
from .personal_information import PersonalInformation
from .limit_mixin import LimitMixin


class EgoMixin(LimitMixin):
    """Bot自我意识混合类"""
    def __init__(
            self, 
            personal_information: Optional[PersonalInformation] = None,
            chat_style: list[str] = ["少量夹杂网络梗"], 
            name: str = "月白", 
            nicknames: list[str] = ["sirius", "胉"], 
            gender: str = "女", 
            species: str = "人类",
            birthday: Optional[str] = "2003-10-24", 
            hobbies: Optional[list[str]] = ["编程", "绘画", "音乐", "游戏"], 
            personality: Optional[str] = ["聪明", "好奇心强但不表现", "要强", "可爱"],
            ):
        LimitMixin.__init__(self)
        if personal_information:
            self._personal_information = personal_information
        else:
            self._personal_information = PersonalInformation(name, nicknames, gender, species, birthday, hobbies, personality)
        self._chat_style = chat_style
        self._prompts.append(self._get_chat_style_prompt())

    def _get_chat_style_prompt(self) -> str:
        if not self._chat_style:
            return ""
        return "在对话中以以下聊天风格回复：" + "、".join(self._chat_style) + "。"

    def get_total_prompt(self) -> str:
        """获取包含个人信息和限制的完整提示词"""
        total_prompt = ""
        total_prompt += self._personal_information._get_pi_prompt()
        for prompt in self.get_limit_prompts():
            total_prompt += prompt
        total_prompt += self._get_chat_style_prompt()
        return total_prompt