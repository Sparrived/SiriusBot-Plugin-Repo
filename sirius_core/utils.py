from ncatbot.core import BaseMessageEvent

def msg_classify(msg : BaseMessageEvent):
    if msg.is_group_msg():
        return msg.group_id, "group"
    else:
        return msg.sender.user_id, "private"