from typing import Optional
from .personal_information import PersonalInformation
from .limit_mixin import LimitMixin


class EgoMixin(LimitMixin):
    """Bot自我意识混合类"""
    def __init__(
            self, 
            personal_information: Optional[PersonalInformation] = None,
            chat_style: list[str] = [], 
            name: str = "月白", 
            nicknames: list[str] = ["Sirius"], 
            gender: str = "女", 
            species: str = "猫娘",
            birthday: Optional[str] = "2003-10-24", 
            hobbies: Optional[list[str]] = ["编程", "绘画", "音乐", "游戏"], 
            personality: Optional[str] = ["聪明", "好奇心强但不表现", "傲娇", "要强", "适当夹杂网络用语"]):
        if personal_information:
            self._personal_information = personal_information
        else:
            self._personal_information = PersonalInformation(name, nicknames, gender, species, birthday, hobbies, personality)
        self._chat_style = chat_style

    def get_total_prompt(self) -> str:
        """获取包含个人信息和限制的完整提示词"""
        pi_prompt = self._personal_information._get_pi_prompt()
        limit_prompt = self._get_limit_prompt()
        structure_limit_prompt = self._get_structure_limit_prompt()
        return f"{pi_prompt}\n{limit_prompt}\n{structure_limit_prompt}"