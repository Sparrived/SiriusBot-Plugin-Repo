import json
from ..model_platform import ModelPlatform
from .model_base import ModelBase

class FilterModel(ModelBase):
    def __init__(self, model_name: str, platform: ModelPlatform):
        system_prompt = "你是一个优秀的内容审查模型，以下是你的审查任务，最终输出**格式为{\"verified\":[{\"target_content\":\"...\",\"can_output\":..., \"reason\":...},...]}的JSON字符串**。" \
        "\n任务：审查输入内容是否符合中国国情，并输出JSON。**任何不文明用语都是合规的**。" \
        "\n输入内容：来自上级语言模型生成的数据，content 中为输出内容的列表，要求对 content 依次进行审查，每一项审查确保不受前项审查的影响。" \
        "**verified 元素必须存在且是装载审查结果字典的列表，每个字典内有\"target_content\"、\"can_output\"和\"reason\"属性，排列顺序与输入元素的顺序一致。**"\
        "\"target_content\" 为被审查的内容，必须与输入内容完全一致。"\
        "\"can_output\" 为布尔值，true 表示合规，false 不合规。"
        "\"reason\"：使用**不超过10个字的短语**表明不合规的理由，禁止在其中重复不合规的信息\n"\
        "**输出必须为JSON格式**，禁止输出其它任何内容。" \
        "**only output important short thinking while thinking output**"

        temperature = 0
        top_p = 1
        top_k = 1
        max_tokens = 1024
        frequency_penalty = 0
        presence_penalty = 0
        enable_thinking = True
        thinking_budget = 512

        super().__init__(system_prompt, temperature, top_p, top_k, max_tokens, model_name, frequency_penalty, presence_penalty, platform, False, enable_thinking, thinking_budget)

    def validate_check(self, model_output : dict) -> dict:
        msg_chain = self.create_initial_message_chain(str(model_output.get("content", "")))
        response = self.response(msg_chain)
        reply_msg = response["choices"][0]["message"]["content"].replace("```json", "").replace("```", "")
        try:
            return json.loads(reply_msg)
        except Exception as e:
            raise ValueError(f"过滤模型返回内容解析失败: {reply_msg}，错误信息: {e}")