from sirius_core.sirius_plugin import SiriusPlugin
from ncatbot.plugin_system import command_registry, admin_only
from ncatbot.core.event import BaseMessageEvent
from .utils import fetch_ip_async, set_new_domain, getDomainInfo



class IPChecker(SiriusPlugin):
    name = "IPChecker"
    version = "1.1.0"
    description = "IP 变更检测插件"

    async def on_load(self):
        super().pre_initialize_plugin()

        # ------- 注册config --------
        self.register_config("last_ip", "", "上一次的IP地址，用于比较是否有变化")
        self.register_config("start_scheduled", True, "是否启动定时检测任务", bool)
        self.register_config("check_interval", 60, "IP检测间隔，单位为秒", int)
        self.register_config("domain_name", "nepholumina.top", "用于更新解析记录的域名")

        # 恢复上次保存的 IP
        self._last_ip = self.config.get("last_ip", None)
        self._check_interval = self.config.get("check_interval", 60)
        # 注册定时检测任务
        if self.config.get("start_scheduled", True):
            self.add_scheduled_task(
                job_func=self._periodic_check,
                name="ip_change_detector",
                interval=f"{self._check_interval}s",
                args=(self._last_ip,)
            )
            self._log.info(f"IP 变更检测任务已启动，每 {self._check_interval} 秒检测一次。")

    @admin_only
    @command_registry.command("主机地址查询", description="获取机器人所在主机的公网 IP")
    async def cmd_ipcheck(self, msg : BaseMessageEvent):
        try:
            ip = await fetch_ip_async()
            await self.message_sender.reply_by_message_event(msg, "command.ipcheck_success", args=ip) # 🌐 让我看看喵！现在的公网IP是 {ip} 喵！
        except Exception as e:
            await self.message_sender.reply_by_message_event(msg, "command.ipcheck_failure", args=str(e)) # ❌ 查询失败了喵.\n{e}

    @admin_only
    @command_registry.command("域名查询", description="获取在主机公网 IP 域名信息")
    async def cmd_domaincheck(self, msg : BaseMessageEvent):
        try:
            info = getDomainInfo()
            await self.message_sender.reply_by_message_event(msg, "command.domaincheck_success", args=info) # 🌐 我知道了喵！以下是域名的状态信息喵~\n{info}
        except Exception as e:
            await self.message_sender.reply_by_message_event(msg, "command.domaincheck_failure", args=str(e)) # ❌ 查询失败了喵.\n{e}

    async def _periodic_check(self, last_ip: str | None):
        self._log.debug("开始检测 IP 变化...")
        try:
            current_ip = await fetch_ip_async()
        except Exception as e:
            self._log.error(f"检测 IP 失败：{e}")
            return

        if last_ip is None:
            self._log.info(f"首次检测到 IP 为 {current_ip}，已记录。")
            self._last_ip = current_ip
            self.config["last_ip"] = current_ip
            return

        if current_ip == last_ip:
            self._log.debug("IP 未变化。")
            return

        self._last_ip = current_ip
        self.config["last_ip"] = current_ip

        # 更新域名解析记录
        try:
            set_new_domain(current_ip)
        except Exception as e:
            self._log.warning(f"更新域名解析记录失败：{e}")

        # 向所有订阅群发送通知
        self._broadcast_ip_change(old_ip=last_ip, new_ip=current_ip)


    def _broadcast_ip_change(self, old_ip: str, new_ip: str):
        event_result = self.publish("SubscriptionHub.QuerySubscribed", {"plugin": "IPChecker"})
        result = event_result[0] if isinstance(event_result, (list, tuple)) else event_result
        subscribed = result.get("subscribed", [])

        for id, target in subscribed:
            try:
                if target == "group":
                    self.message_sender.post_group_message(self.api, id, "command.ip_change_notification", args=(old_ip, new_ip, self.config.get('domain_name', 'nepholumina.top')))
                elif target == "private":
                    self.message_sender.post_private_message(self.api, id, "command.ip_change_notification", args=(old_ip, new_ip, self.config.get('domain_name', 'nepholumina.top')))
            except Exception as e:
                self._log.error(f"向 {target} {id} 发送通知失败：{e}")
