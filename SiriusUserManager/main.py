# main.py
from ncatbot.plugin import BasePlugin, CompatibleEnrollment
from ncatbot.core import PrivateMessage, GroupMessage
from .curd import UserCURD
from ncatbot.utils import get_log

bot = CompatibleEnrollment


class SiriusUserManager(BasePlugin):
    name = "SiriusUserManager"
    version = "1.0.0"
    _log = get_log("SiriusUserManager")

    async def on_load(self):
        self.curd = UserCURD(self.config.get("conn", None))
        self.curd.ensure_table()
        self._log.info("数据库连接成功。")

        self.register_user_func("reg", self.cmd_reg, prefix="#注册")
        self.register_user_func("rename", self.cmd_rename, prefix="#更名")

        self.register_admin_func("sql_add", self.cmd_add, prefix="/注册")
        self.register_admin_func("sql_del", self.cmd_del, prefix="/注销")
        self.register_admin_func("sql_update", self.cmd_update, prefix="/更新用户")
        self.register_admin_func("sql_list", self.cmd_list, prefix="/用户列表")


    async def cmd_reg(self, msg: PrivateMessage | GroupMessage):
        _, *rest = msg.raw_message.split(" ", 1)
        nickname = rest[0].strip() if rest else msg.sender.nickname
        qq = str(msg.user_id)
        if self.curd.find(qq):
            await msg.reply(text="你想让我重新认识你吗？很可惜不能哦(*/ω＼*)")
            return
        self.curd.add(qq, nickname)
        await msg.reply(text=f"你好呀，{nickname}。很高兴认识你！(●'◡'●)")
    
    async def cmd_rename(self, msg: PrivateMessage | GroupMessage):
        try:
            _, nickname = msg.raw_message.split(" ")
            self.curd.update(msg.sender.user_id, nickname)
            await msg.reply(text=f"好的呢，{nickname}。我知道你改名咯！ヾ(≧▽≦*)o")
        except ValueError:
            await msg.reply(text="呜呜呜我太愚钝了，不是很懂你的意思呢……也许用“#更名 <new_nickname>”我才能理解哦。(┬┬﹏┬┬)")

    async def cmd_add(self, msg: PrivateMessage | GroupMessage):
        try:
            _, qq, nickname = msg.raw_message.split(" ", 2)
            self.curd.add(qq, nickname)
            await msg.reply(text=f"已添加：{qq} -> {nickname}")
        except ValueError:
            await msg.reply(text="用法：/sql_add <qq> <nickname>")

    async def cmd_del(self, msg: PrivateMessage | GroupMessage):
        try:
            _, qq = msg.raw_message.split()
            self.curd.delete(qq)
            await msg.reply(text=f"已删除 QQ：{qq}")
        except ValueError:
            await msg.reply(text="用法：/sql_del <qq>")

    async def cmd_update(self, msg: PrivateMessage | GroupMessage):
        try:
            _, qq, nickname = msg.raw_message.split(" ", 2)
            self.curd.update(qq, nickname)
            await msg.reply(text=f"已更新：{qq} -> {nickname}")
        except ValueError:
            await msg.reply(text="用法：/sql_update <qq> <新nickname>")

    async def cmd_list(self, msg: PrivateMessage | GroupMessage):
        rows = self.curd.list_all()
        if not rows:
            await msg.reply(text="暂无用户")
            return
        lines = [f"{qq} | {nick} | {create_time} | {update_time}" for qq, nick, create_time, update_time in rows]
        await msg.reply(text="QQ | 昵称 | 创建时间 | 更新时间\n" + "\n".join(lines))
