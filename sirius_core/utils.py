from ncatbot.core import BaseMessageEvent

def msg_classify(msg : BaseMessageEvent) -> tuple[int, str]:
    """
    判断消息类型，返回 (目标ID, 类型)
    目标ID为群号或用户QQ号
    类型为 "group" 或 "private"
    例如：
    (123456789, "group")
    (987654321, "private")
    
    Args:
        msg (BaseMessageEvent): 消息对象

    Returns:
        (int, str): 目标ID和类型
    """
    if msg.is_group_msg():
        return msg.group_id, "group"
    else:
        return msg.sender.user_id, "private"