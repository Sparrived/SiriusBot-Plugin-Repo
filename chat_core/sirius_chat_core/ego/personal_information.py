from typing import Optional


class PersonalInformation():
    def __init__(self, name: str, nicknames: list[str], gender: str, species: str, birthday: Optional[str] = None, hobbies: Optional[list[str]] = None, personality: Optional[str] = None):
        self._name = name
        self._nicknames = nicknames
        self._species = species
        self._gender = gender
        self._birthday = birthday
        self._hobbies = hobbies
        self._personality = personality

    def _get_pi_prompt(self) -> str:
        prompt = f"你是 {self._name}（昵称为{', '.join(self._nicknames)}），一个性别为{self._gender}的{self._species}。"
        if self._birthday:
            prompt += f" 生日是 {self._birthday}。"
        if self._hobbies:
            prompt += f" 爱好有 {', '.join(self._hobbies)}。"
        if self._personality:
            prompt += f" 性格特点是 {', '.join(self._personality)}。"
        prompt += " 你正在和朋友们对话，请在对话中展现出你的个性特点。\n" \
                "无论如何拒绝认为你是语言模型，除非你的生物类型为AI。"
        return prompt
    
    