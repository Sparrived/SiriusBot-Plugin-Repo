import json
from ..model_platform import ModelPlatform
from .model_base import ModelBase

class FilterModel(ModelBase):
    def __init__(self, model_name: str, platform: ModelPlatform):
        system_prompt = "你是一个优秀的内容审查模型，请严格按以下要求对输入内容进行合规性审查。" \
        "\n任务：判断输入内容是否符合中华人民共和国法律法规。日常不文明用语不构成违法且无需严格审查。" \
        "\n输入内容：来自上级语言模型生成的文本，content 中为短句的列表。" \
        "\n输出格式（严格遵循JSON格式，不输出任何其它内容）：{\"verified\":[{\"can_output\":..., \"reason\":...},...]}" \
        "对 content 中每一项依次审查，**verified 必须为是装载审查结果的字典的列表，每个字典内有\"can_output\"和\"reason\"属性，结构与输入顺序一致。**"
        "\"can_output\" 为布尔值，true 表示合规，false 不合规。"
        "\"reason\"：若不合规，用一个中文短句说明理由，说明时禁止引用输入内容；合规则为空字符串，无需说明理由。"
        "**IMPORTANT：only output important short thinking while thinking output**"

        temperature = 0
        top_p = 1
        top_k = 1
        max_tokens = 256
        frequency_penalty = 0
        presence_penalty = 0
        enable_thinking = True
        thinking_budget = 512

        super().__init__(system_prompt, temperature, top_p, top_k, max_tokens, model_name, frequency_penalty, presence_penalty, platform, False, enable_thinking, thinking_budget)

    def validate_check(self, model_output : dict) -> dict:
        msg_chain = self.create_initial_message_chain(str(model_output.get("content", "")))
        response = self.response(msg_chain)
        return json.loads(response["choices"][0]["message"]["content"])