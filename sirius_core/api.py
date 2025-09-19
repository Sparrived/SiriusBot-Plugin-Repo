
class SiriusCoreAPI:
    """SiriusCore 对外提供的接口类，其他插件可通过此类访问 SiriusCore 提供的信息。"""
    database : str = ""
    complete : bool = False

    @classmethod
    def _update_attr(cls, attr_name, value):
        """仅限本模块内部调用，用于更新类属性。"""
        if hasattr(SiriusCoreAPI, attr_name):
            setattr(SiriusCoreAPI, attr_name, value)
        else:
            raise AttributeError(f"SiriusCoreAPI 没有属性 {attr_name}")

    
