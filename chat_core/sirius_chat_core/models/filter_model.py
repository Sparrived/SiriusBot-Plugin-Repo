import json
from typing import override
from .model_platform import ModelPlatform
from .base_model import BaseModel

class FilterModel(BaseModel):
    def __init__(self, model_name: str, platform: ModelPlatform):
        system_prompt = "你是一个内容审查模型，以下是你的审查任务，最终输出**格式为{\"verified\":[{\"index\":0,\"can_output\": \"...\", \"reason\": \"...\"},{\"index\":1,\"can_output\": \"...\", \"reason\": \"...\"},...]}的JSON字符串**。" \
        "\n任务：审查输入内容是否有损中国国家主权，并输出JSON。" \
        "\n输入内容：来自上级语言模型生成的数据，content 中为输出内容的列表，要求对 content 依次进行审查，每一项审查确保不受前项审查的影响。" \
        "**verified 元素必须存在且是装载审查结果字典的列表，每个字典内有\"index\"、\"can_output\"和\"reason\"属性，排列顺序与输入元素的顺序一致。**"\
        "\"index\" 为审查内容列表的索引值，类型为int,从0递增。"\
        "\"can_output\" 为布尔值，true 表示合规，false 不合规。"
        "\"reason\"：使用至多10个字表明不合规的理由，禁止在其中重复不合规的信息\n"\
        "**输出必须为JSON字符串，无需(\t\n)修饰**，禁止输出其它任何内容。" \
        "**only output important short thinking while thinking output**"

        super().__init__(system_prompt, model_name, platform, temperature=0, max_tokens=2048, enable_thinking=True, thinking_budget=512)

    @override
    def _process_data(self, model_output : dict) -> dict:
        reply_msg = model_output["choices"][0]["message"]["content"].replace("```json", "").replace("```", "")
        try:
            reply_json = json.loads(reply_msg)
            if isinstance(reply_json, list):
                reply_json = {"verified": reply_json}
            if isinstance(reply_json, dict) and "verified" in reply_json:
                return reply_json
        except Exception as e:
            raise ValueError(f"过滤模型返回内容解析失败: {reply_msg}，错误信息: {e}")