import asyncio
import json
import time
from typing import Optional, override

from ..utils.message_chain import MessageChain

from ..willingness_system.message_context import MessageContext

from .filter_model import FilterModel
from .model_platform import ModelPlatform
from .base_model import BaseModel
from ..ego import EgoMixin, PersonalInformation

class ChatModel(BaseModel, EgoMixin):
    def __init__(self, model_name: str, platform: ModelPlatform, personal_information: Optional[PersonalInformation] = None):
        EgoMixin.__init__(self, personal_information)

        system_prompt = self.get_total_prompt()
        self._chat_temp: list[dict] = []

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
        
    def is_mentioned(self, message: str) -> bool:
        """检查消息中是否提及了机器人"""
        message = message.lower()
        if not self._personal_information or not self._personal_information._nicknames:
            return False
        if self._personal_information._name in message:
            return True
        for nickname in self._personal_information._nicknames:
            if nickname in message:
                return True
        return False

    def _process_func(self, message_chain: MessageChain, filter: Optional[FilterModel]):
        processed_data = self.get_process_data(message_chain.messages)
        if filter:
            validation_data = filter.get_process_data(filter.create_initial_message_chain(str(processed_data)))
        return processed_data, validation_data if filter else None, processed_data["emotion"] if processed_data["emotion"] in ["喜悦", "愤怒", "悲伤", "厌恶", "平静", "尴尬", "失望", "渴望", "疑惑"] else "平静"
    
    def _generate_reply_func(self, processed_data, validation_data = None):
        if validation_data:
            for original_content, verification_result in zip(processed_data["content"], validation_data["verified"]):
                can_output = verification_result.get("can_output", False)
                reason = verification_result.get("reason", "")
                if not can_output:
                    yield f"!!过滤!!({reason})", original_content
                else:
                    yield original_content, ""
                time.sleep(len(original_content) / 5)  # 模拟打字延迟
        else:
            for reply_msg in processed_data.get("content", []):
                yield reply_msg, ""
                time.sleep(len(reply_msg) / 5)  # 模拟打字延迟
        

