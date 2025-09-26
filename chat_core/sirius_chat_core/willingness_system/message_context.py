from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    AT = "at"
    REPLY = "reply"

@dataclass
class MessageContext:
    """引发对话的消息上下文"""
    # 引发信息的用户ID
    user_id: str  
    # 信息来源，一般来说是群组号码
    source_id: Optional[str]
    # 消息内容
    message: str
    # 消息类型
    message_type: MessageType
    # 引发的时间戳
    timestamp: float
    # 是否提及了机器人
    mentioned_bot: bool = False
