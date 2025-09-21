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