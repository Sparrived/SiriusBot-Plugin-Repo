from ncatbot.plugin_system import NcatBotPlugin, NcatBotEvent
from ncatbot.plugin_system import command_registry, admin_only
from ncatbot.core.event import BaseMessageEvent
from ncatbot.utils import get_log
from .utils import fetch_ip_async, set_new_domain, getDomainInfo

CHECK_INTERVAL = 1 * 60


class IPChecker(NcatBotPlugin):
    name = "IPChecker"
    version = "1.1.0"
    author = "Sparrived"
    description = "IP 变更检测器"
    _log = get_log("IPChecker")

    async def on_load(self):
        self.register_config("last_ip", "", "上一次的IP地址，用于比较是否有变化")
        # 恢复上次保存的 IP
        self._last_ip = self.config.get("last_ip", None)
        # 注册定时检测任务
        self.add_scheduled_task(
            job_func=self._periodic_check,
            name="ip_change_detector",
            interval=f"{CHECK_INTERVAL}s",
            args=(self._last_ip,)
        )
        self._log.info("IP 变更检测任务已启动，每 %d 秒检测一次。" % CHECK_INTERVAL)

    @admin_only
    @command_registry.command("ipcheck", description="获取机器人所在主机的公网 IP")
    async def cmd_ipcheck(self, msg : BaseMessageEvent):
        try:
            ip = fetch_ip_async()
            await msg.reply(text=f"🌐 让我看看喵！现在的公网IP是 {ip} 喵！")
        except Exception as e:
            await msg.reply(text=f"❌ 查询失败了喵.\n{e}")

    @admin_only
    @command_registry.command("domaincheck", description="获取在主机公网 IP 域名信息")
    async def cmd_domaincheck(self, msg : BaseMessageEvent):
        try:
            info = getDomainInfo()
            await msg.reply(text=f"🌐 我知道了喵！以下是域名的状态信息喵~\n{info}")
        except Exception as e:
            await msg.reply(text=f"❌ 查询失败了喵.\n{e}")

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
            self._log.error(f"更新域名解析记录失败：{e}")

        # 向所有订阅群发送通知
        self._broadcast_ip_change(old_ip=last_ip, new_ip=current_ip)


    def _broadcast_ip_change(self, old_ip: str, new_ip: str):
        event_result = self.publish("SubscriptionHub.QuerySubscribedGroups", {"plugin": "IPChecker"})
        result = event_result[0] if isinstance(event_result, (list, tuple)) else event_result
        groups = result.get("subscribed", [])

        msg_text = (
            "⚠️ 提醒一下大家，服务器的 IP 变化了喵！\n"
            f"旧 IP：{old_ip}\n"
            f"新 IP：{new_ip}\n"
            f"如果服务器连接不上，请使用新 IP 或者使用 nepholumina.top 进行连接喵~"
        )

        for gid in groups:
            try:
                self.api.post_group_msg_sync(group_id=gid, text=msg_text)
            except Exception as e:
                self._log.error(f"[IPCheck] 向群 {gid} 发送通知失败：{e}")
