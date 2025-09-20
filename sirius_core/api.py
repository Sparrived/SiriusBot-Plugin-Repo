
from typing import LiteralString, Optional


class SiriusCoreAPI:
    """SiriusCore 对外提供的接口类，其他插件可通过此类访问 SiriusCore 提供的信息。"""
    database : str = ""
    complete : bool = False

    @classmethod
    async def get_subscribed(cls, instance, target: Optional[LiteralString] = None, args: dict = None) -> dict:
        """获取某插件的订阅信息。

        Args:
            instance: 插件实例
            target: 订阅目标，可选
            args: 传入的额外参数，可选

        Returns:
            包含插件订阅信息的字典，格式如下：
            {
                "plugin": <插件名称>,
                "subscribed": <订阅信息列表> （如果target为None，此处为List[tuple]）,
                "args": <传入的额外参数>
            }
        """
        if not cls.complete:
            raise RuntimeError("SiriusCoreAPI 未初始化完成，无法调用此方法。")
        event_result = await instance.publish("SubscriptionHub.QuerySubscribed", {"plugin": instance.name, "target": target, "args": args})
        event_result = event_result[0] if isinstance(event_result, list) else event_result
        return event_result


    @classmethod
    def _update_attr(cls, attr_name, value):
        """仅限本模块内部调用，用于更新类属性。"""
        if hasattr(SiriusCoreAPI, attr_name):
            setattr(SiriusCoreAPI, attr_name, value)
        else:
            raise AttributeError(f"SiriusCoreAPI 没有属性 {attr_name}")

    
