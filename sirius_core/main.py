from typing import Optional
from ncatbot.plugin_system import NcatBotEvent
from ncatbot.plugin_system import admin_only
from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent, BaseSender
from .curd import HubCURD
from .utils import msg_classify
from .sirius_plugin import SiriusPlugin
from .data_process import init_database, init_filetext

class SiriusCore(SiriusPlugin):
    name = "SiriusCore"
    version = "1.1.0"
    description = "SiriusBot 及其各项插件的核心桥接器."
    dependencies = {}

    async def on_load(self):
        # -------- 注册config --------
        self.register_config("data_save_type", "sqlserver", "数据保存方式，支持 sqlserver/textfile")
        self.register_config("sql_settings",
                              {
                                "server": "127.0.0.1",
                                "port": 9981,
                                "database": "SampleDB",
                                "UID": "sa",
                                "PWD": "yourStrong(!)Password"
                              }, 
                              "数据库连接相关参数，仅在 data_save_type 为 sqlserver 时有效")
        
        # -------- 检查config --------
        result_msg, is_valid = self._check_config(self.config.get("data_save_type", None))
        if not is_valid:
            self._log.error(f"配置错误：{result_msg}，插件不再继续运行。")
            return
        


        self.curd = HubCURD(self.config.get("conn", None))
        self.curd.ensure_table()
        self._log.info("数据库连接成功。")
        self.register_handler("SubscriptionHub.QuerySubscribedGroups", self.on_query_subscribed_groups)
        self._log.info("开始监听 SubscriptionHub.QuerySubscribedGroups.")
        self.register_handler("SubscriptionHub.QuerySubscribedPrivate", self.on_query_subscribed_private)
        self._log.info("开始监听 SubscriptionHub.QuerySubscribedPrivate.")

    def _check_config(self, data_save_type : Optional[str]) -> tuple[str, bool]:
        """
        检查配置中的数据保存方式是否合法，并初始化数据库连接（如适用）。
        Args:
            data_save_type (str | None): 数据保存方式，支持 'sqlserver' 或 'textfile'。
        Returns:
            (str, bool): 
                - 如果配置合法，返回连接字符串或相关信息，以及 True。
                - 如果配置不合法，返回问题描述字符串，以及 False。
        """
        result_msg = ""
        if not data_save_type:
            result_msg = "未在config中配置数据保存方式"
            return result_msg, False
        if data_save_type not in ("sqlserver", "textfile"):
            result_msg = "数据保存方式仅支持 'sqlserver' 或 'textfile'"
            return result_msg, False
        
        if data_save_type in ("sqlserver",):
            sql_settings = self.config.get("sql_settings", None)
            result_msg, is_valid = init_database(sql_settings, data_save_type)
        elif data_save_type == "textfile":
            result_msg, is_valid = init_filetext()
            # TODO : textfile的处理方式
            pass
        
        return result_msg, is_valid



    @admin_only
    @command_registry.command("订阅", description="订阅插件")
    async def cmd_sub(self, msg: BaseMessageEvent, plugin_name : str):
        id, target = msg_classify(msg)
        self.curd.add_sub(plugin_name, id, target)
        await msg.reply(text=f"嗨嗨嗨~我知道了！这里以后开始执行 {plugin_name} 的功能喵！=w=")

    @admin_only
    @command_registry.command("取消订阅", description="取消订阅插件")
    async def cmd_unsub(self, msg: BaseMessageEvent, plugin_name : str):
        id, target = msg_classify(msg)
        self.curd.remove_sub(plugin_name, id, target)
        await msg.reply(text=f"蒜鸟蒜鸟,这里以后不再执行 {plugin_name} 的功能了喵！＞﹏＜")

    @command_registry.command("插件订阅列表", description="查看已经订阅的插件列表")
    async def cmd_list(self, msg: BaseMessageEvent):
        id, target = msg_classify(msg)
        plugins = self.curd.list_by_target_id(id, target)
        if not plugins:
            await msg.reply(text="这里竟然没有任何插件订阅喵，这让我显得很没有用武之地喵！╰（‵□′）╯")
        else:
            await msg.reply(text="这些插件功能已经启动了喵！\\(￣︶￣*\\))\n" + "\n".join(plugins))

    async def on_query_subscribed_groups(self, event : NcatBotEvent):
        plugin = event.data["plugin"]
        subscribed = self.curd.list_by_plugin_groups(plugin)
        args = {}
        if event.data:
            args = event.data.get("args", {})
        event.add_result({"plugin": plugin, "subscribed": subscribed, "args": args})

    async def on_query_subscribed_private(self, event : NcatBotEvent):
        plugin = event.data["plugin"]
        subscribed = self.curd.list_by_plugin_private(plugin)
        args = {}
        if event.data:
            args = event.data.get("args", {})
        event.add_result({"plugin": plugin, "subscribed": subscribed, "args": args})
