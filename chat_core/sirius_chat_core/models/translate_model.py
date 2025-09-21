import json
from .model_platform import ModelPlatform
from .model_base import BaseModel

class TranslateModel(BaseModel):
    def __init__(self, model_name: str, platform: ModelPlatform):
        system_prompt = "你是一个优秀的翻译模型，你需要判断传入内容是否全部为中文，如果不是则将其翻译为**中文**。\n" \
            "最终输出**格式为{\"need_translate\": bool,\"translated\":{\"source_content\":\"...\",\"target_content\":\"...\"},...}的JSON字符串**。" \
            "其中，\"need_translate\"表示是否需要翻译，true表示有，false表示没有。" \
            "\"translated\"为一个字典，包含\"source_content\"和\"target_content\"两个属性，分别表示原始内容和翻译后的内容。" \
            "\"source_content\"必须与输入内容完全一致。" \
            "\"target_content\"是翻译后的内容，必须为中文。" \
            "**输出必须为JSON格式**，禁止输出其它任何内容。" \

        temperature = 0.5
        top_p = 0.9
        top_k = 1
        max_tokens = 1024
        frequency_penalty = 0
        presence_penalty = 0
        enable_thinking = True
        thinking_budget = 512

        super().__init__(system_prompt, temperature, top_p, top_k, max_tokens, model_name, frequency_penalty, presence_penalty, platform, False, enable_thinking, thinking_budget)

    def translate(self, model_output : dict) -> dict:
        msg_chain = self.create_initial_message_chain(str(model_output.get("content", "")))
        response = self.response(msg_chain)
        reply_msg = response["choices"][0]["message"]["content"].replace("```json", "").replace("```", "")
        try:
            return json.loads(reply_msg)
        except Exception as e:
            raise ValueError(f"翻译模型返回内容解析失败: {reply_msg}，错误信息: {e}")