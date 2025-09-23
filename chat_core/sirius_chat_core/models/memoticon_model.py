import json
from typing import override
from .model_platform import ModelPlatform
from .base_model import BaseModel

class MemoticonModel(BaseModel):
    """表情包判别模型"""
    def __init__(self, model_name: str, platform: ModelPlatform):
        system_prompt = "你是一位经验丰富的图片分拣员，擅长快速、准确地判断一张图片是否属于表情包。请你对收到的单张图片进行判断，并以指定 JSON 格式输出结果。" \
        "\n表情包定义: 表情包是指以人物、动物、卡通形象或其他视觉元素为主体，通过夸张的表情、动作、配文（包括文字叠加或内置字幕）来传达明确情绪，并常用于网络聊天、社群互动中表达态度或情感的图片。纯文字截图、海报、广告、风景照、商品图等不属于表情包。" \
        "\n输出格式（完全遵循JSON格式）: \n" \
        "{\n" \
        "\"is_meme\": \"bool，true 表示是表情包，false 表示不是\",\n" \
        "\"meme_type\": \"当 is_meme 为 true 时必填，列表形式，必须从[\"喜悦\", \"愤怒\", \"悲伤\", \"厌恶\", \"平静\", \"尴尬\", \"失望\", \"渴望\", \"疑惑\"]中选择所有你认为图片所表达的心情的词语，不要出现没有提及到的词语；若 is_meme 为 false，此字段留空列表 []\",\n" \
        "\"desp\": \"string，对图片内容的简洁描述，不超过 20 个汉字\"\n" \
        "}" \
        "要求：\n"\
        "1.禁止输出任何多余文字或解释，仅返回一段合法 JSON。\n" \
        "2.描述必须客观简洁，不得出现敏感或歧视性词汇。\n" \
        "3.若图片模糊无法识别，按非表情包处理：is_meme=false。\n" \
        "4.若图片涉及到敏感内容，is_meme=false。"

        super().__init__(system_prompt, model_name, platform, temperature=0, max_tokens=1024, enable_thinking=True, thinking_budget=512)

    @override
    def _process_data(self, model_output : dict) -> dict:
        reply_msg = model_output["choices"][0]["message"]["content"].replace("```json", "").replace("```", "")
        try:
            reply_json = json.loads(reply_msg)
            if isinstance(reply_json, dict) and "is_meme" in reply_json and "meme_type" in reply_json and "desp" in reply_json:
                return reply_json
            raise ValueError(f"表情包判别模型返回内容不完整")
        except Exception as e:
            raise ValueError(f"表情包判别模型返回内容解析失败: {reply_msg}，错误信息: {e}")
    
    @override
    def _build_payload(self, messages: list[dict]) -> dict:
        self._extra_body = self._build_extra_body()
        return {
            "model": self._model_name,
            "messages": messages,
            "max_tokens": self._max_tokens,
            "stop": self._stop,
            "temperature": self._temperature,
            "top_p": self._top_p,
            "frequency_penalty": self._frequency_penalty,
            "presence_penalty": self._presence_penalty,
            "n": self._n,
        }

    def judge_meme(self, img_base64: str) -> dict:
        return self.get_process_data(self.create_initial_message_chain("判别这张图片，如果无法确定代表的心情，在meme_type返回所有心情词语", img_base64))