from typing import Optional
from ncatbot.core.event.message_segment.message_segment import MessageSegment
from ncatbot.core import BaseMessageEvent
from ncatbot.utils import status

def get_message_type(message_segment: MessageSegment):
    """获取消息类型，返回 "at", "text", "image", "video", "record", "music", "share", "reply" 或 "unknown" """
    if message_segment.msg_seg_type not in ["at", "text", "image", "video", "record", "music", "share", "reply"]:
        return "unknown"
    return message_segment.msg_seg_type

async def send_message(target: str, target_id: str, content: Optional[str] = None, image: Optional[str] = None):
    """根据消息发送来源发送消息"""
    if target == "group":
        await status.global_api.post_group_msg(target_id, content, image=image)
    elif target == "private":
        await status.global_api.post_private_msg(target_id, content, image=image)
    else:
        raise ValueError("未知的消息发送目标")
    

def get_target_str(msg: BaseMessageEvent):
    if msg.is_group_msg():
        target = "G"+msg.group_id
        user_card = msg.sender.card
    else:
        target = "P"+msg.user_id
        user_card = ""
    return target, user_card

    
