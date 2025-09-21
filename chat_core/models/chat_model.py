from typing import Optional
from ..model_platform import ModelPlatform
from .model_base import ModelBase
from ..ego import EgoMixin, PersonalInformation

class ChatModel(ModelBase, EgoMixin):
    def __init__(self, model_name: str, platform: ModelPlatform, personal_information: Optional[PersonalInformation] = None):
        EgoMixin.__init__(self, personal_information)

        system_prompt = self.get_total_prompt()
        temperature = 0.7
        top_p = 0.9
        max_tokens = 512
        frequency_penalty = 0.3
        presence_penalty= 0.3

        ModelBase.__init__(self,system_prompt, temperature, top_p, 0, max_tokens, model_name, frequency_penalty, presence_penalty, platform)
