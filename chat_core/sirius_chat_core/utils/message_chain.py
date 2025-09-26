from typing import Optional


class MessageChain:
    """消息链"""
    _messages: list[dict]

    def __init__(self, messages: list[dict]):
        """初始化一个消息链"""
        if not messages or not isinstance(messages, list):
            raise ValueError("消息链不能为空，且必须为列表")
        if not all(isinstance(m, dict) and "role" in m and "content" in m for m in messages):
            raise ValueError("消息链中的每个消息必须是包含'role'和'content'字段的字典")
        if messages[0].get("role") != "system":
            raise ValueError("消息链的第一条消息必须是系统消息，role 必须为 'system'")
        self._messages = messages
    
    @property
    def messages(self) -> list[dict]:
        if len(self._messages) > 1 and self._messages[-1].get("role") != "user":
            raise ValueError("消息链的最后一条消息必须是用户消息，role 必须为 'user'")
        return self._messages
    
    def __iter__(self):
        return iter(self._messages)

    def __getitem__(self, index):
        return self._messages[index]
    
class MessageChainBuilder:
    _messages: list[dict]
    def __init__(self):
        self._messages = []

    @classmethod
    def from_message_chain(cls, message_chain: MessageChain):
        """从消息链创建构建器"""
        builder = cls()
        builder._messages = message_chain.messages
        return builder

    def create_new_message_chain(self, system_prompt: str):
        """构建消息链"""
        self._messages.append({"role": "system", "content": system_prompt})

    def add_user_message(self, content: str, img_base64: Optional[str] = None):
        """添加用户消息到消息链"""
        if self._messages is None:
            self._messages = []
        if len(self._messages) > 1 and self._messages[-1]["role"] == "user":
            raise ValueError("用户消息不能连续发送")
        if img_base64:
            self._messages.append({"role": "user",
                                    "content": [{"type": "image_url", 
                                         "image_url":{
                                             "url": f"data:image/jpeg;base64,{img_base64}",
                                             "detail":"low"
                                             }
                                        }, 
                                    {"type": "text", "text": content}]})
        else:
            self._messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str):
        """添加助手消息到消息链"""
        if self._messages is None:
            self._messages = []
        if len(self._messages) > 1 and self._messages[-1]["role"] == "assistant":
            raise ValueError("助手消息不能连续发送")
        self._messages.append({"role": "assistant", "content": content})
    
    def clear_message_chain(self):
        """清空消息链"""
        self._messages = []
    
    def build(self) -> MessageChain:
        """得到消息链字符串,并清空当前消息链"""
        if not self._messages:
            raise ValueError("消息链为空，请先添加消息")
        messages = self._messages
        self.clear_message_chain()
        return MessageChain(messages)