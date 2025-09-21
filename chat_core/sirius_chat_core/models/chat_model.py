import json
from typing import Optional, override
from .model_platform import ModelPlatform
from .base_model import BaseModel
from ..ego import EgoMixin, PersonalInformation

class ChatModel(BaseModel, EgoMixin):
    def __init__(self, model_name: str, platform: ModelPlatform, personal_information: Optional[PersonalInformation] = None):
        EgoMixin.__init__(self, personal_information)

        system_prompt = self.get_total_prompt()

        BaseModel.__init__(self, system_prompt, model_name, platform, temperature=0.7, top_p= 0.9, max_tokens=2048)

    @override
    def _process_data(self, model_output: dict) -> dict:
        try:
            content = json.loads(model_output["choices"][0]["message"]["content"])
            if isinstance(content, dict):
                return content
            raise ValueError("无效的响应格式")
        except Exception as e:
            raise ValueError(f"处理数据失败: {e}")