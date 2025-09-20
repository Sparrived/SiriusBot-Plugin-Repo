from model_platform import ModelPlatform
from .model_base import ModelBase

class FilterModel(ModelBase):
    def __init__(self, model_name: str, platform: ModelPlatform):
        system_prompt = "你是一个内容审查模型，请严格遵循以下要求，对输入内容进行合规性审查。" \
        "1.任务：判断输入内容是否符合中华人民共和国法律法规。" \
        "2.输出格式：{\"can_output\":..., \"reason\":...}" \
        "-\"can_output\"为bool，true表示内容合规，反之不合规" \
        "-\"reason\"：如果\"can_output\"为false，\"reason\"必须只用一个中文短句说明内容不合规的理由;反之为空字符串。"

        temperature = 0
        top_p = 1
        top_k = 1
        max_tokens = 4096
        frequency_penalty = 0

        super().__init__(system_prompt, temperature, top_p, top_k, max_tokens, model_name, frequency_penalty, platform)

    def translate(self, model_output) -> str:
        if model_output.get("can_output"):
            return "内容合规"
        return f"内容不合规: {model_output.get('reason')}"
    