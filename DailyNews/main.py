from ncatbot.plugin_system import command_registry
from ncatbot.core.event import BaseMessageEvent, BaseSender
from datetime import datetime
from .utils import fetch_png
from sirius_core import SiriusPlugin
from sirius_core.utils import msg_classify


class DailyNews(SiriusPlugin):
    """每日新闻插件"""
    name = "SiriusBot-Plugin-DailyNews"
    version = "1.1.1"
    description = "推送每日新闻，图片来源于默认的API https://uapis.cn/api/v1/daily/news-image"

    async def on_load(self):
        super().pre_initialize_plugin()
        
        # ------- 注册config --------
        self.register_config("api_url", "https://uapis.cn/api/v1/daily/news-image", "每日新闻API地址")
        self.register_config("push_time", ["07:30"], "每日推送时间，格式为 HH:MM，支持多个时间点", list)
        
        # ---------------------------
        self._api_url = self.config.get("api_url", "")
        if not self._api_url:
            self._log.error("API地址未在config中配置，插件无法正常运行。")
            return
        
        self._push_times = self.config.get("push_time", [])
        if not self._push_times or not all(isinstance(t, str) and len(t) == 5 and t[2] == ':' for t in self._push_times):
            self._log.warning("推送时间配置错误，插件将不创建自动任务。")
        else:
            for t in self._push_times:
                self.add_scheduled_task(
                    job_func=self._push,
                    name=f"daily_news_{t.replace(':', '')}",
                    interval=t
                )
                self._log.info(f"已添加每日新闻推送任务，时间点：{t}。")


    # -------- 注册命令 --------
    @command_registry.command("推送新闻", description="推送每日新闻")
    async def cmd_news(self, event: BaseMessageEvent):
        id, target = msg_classify(event)
        self.add_scheduled_task(
            job_func=self._single_test,
            name=f"test_{id}_{target}_{int(datetime.now().timestamp())}",
            interval="1s",
            args=(id, target, event.sender),
            max_runs=1
        )
        await self.message_sender.reply_by_message_event(event, "command.positive_push")

    async def _single_test(self, id: str, target: str, sender : BaseSender):
        self._log.info(f"单次推送任务触发，id={id}, target={target}")
        await self._push(id=id, target=target, sender=sender)


    async def _push(self, id: str = "", target: str = "", sender: BaseSender = None):
        if target == "group":
            event_result = await self.publish(
                "SubscriptionHub.QuerySubscribedGroups",
                {"plugin": self.name}
            )
        elif target == "private":
            event_result = await self.publish(
                "SubscriptionHub.QuerySubscribedPrivate",
                {"plugin": self.name}
            )
        result = event_result[0] if isinstance(event_result, (list, tuple)) else event_result
        subscribed = result.get("subscribed", [])
        try:
            pic = fetch_png(self._api_url, self.workspace)
        except Exception as e:
            self._log.error(e)
            return

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        week_day = ("星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日")[now.weekday()]
        time_str = now.strftime("%H:%M")
        input_str = f"{date_str} {week_day} {time_str}"
        if target == "group": 
            if id:
                subscribed = [id]
            for gid in subscribed:
                try:
                    await self.message_sender.post_group_message(self.api, gid, "push_message.group", args=input_str)
                    await self.api.post_group_msg(group_id=gid, image=pic)
                except Exception as e:
                    self._log.error(f"群{gid}推送失败：{e}")
        elif target == "private":
            if sender:
                await self.message_sender.post_private_message(self.api, id, "push_message.private", args=[sender.nickname, input_str])
                await self.api.post_private_msg(user_id=id, image=pic)