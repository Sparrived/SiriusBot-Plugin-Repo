# plugins/MinecraftStatus/main.py
import aiohttp
from ncatbot.plugin import BasePlugin, CompatibleEnrollment
from ncatbot.core import GroupMessage, PrivateMessage
from ncatbot.core import MessageChain, Text, Image
import json
import base64
from io import BytesIO
from PIL import Image as PILImage
import asyncio
from ncatbot.utils import get_log

bot = CompatibleEnrollment

class McStatus(BasePlugin):
    name = "McStatus"
    version = "1.0.0"
    _log = get_log("McStatus")
    
    async def on_load(self):
        self.api_url = "https://uapis.cn/api/v1/game/minecraft/serverstatus"
        # 注册用户功能
        self.register_user_func(
            name="mcstatus",
            handler=self.query_server_status,
            prefix="#MC服务器状态",
            description="查询Minecraft服务器状态",
            usage="#MC服务器状态 <服务器地址>",
            examples=["#MC服务器状态 mc.hypixel.net", "#MC服务器状态 192.168.1.1:25565"]
        )
    
    async def query_server_status(self, message):
        """查询Minecraft服务器状态"""
        # 提取服务器地址
        text = message.raw_message.replace("#MC服务器状态", "").strip()
        
        if not text:
            await message.reply(text="看不懂喵╰（‵□′）╯，正确的食用方法是\"#mcstatus <服务器地址>\"喵~")
            return
        
        try:
            # 调用API查询服务器状态
            status_info = await self.get_server_status(text)
            
            if status_info:
                # 生成状态卡片
                card = await self.create_status_card(status_info)
                await message.reply(rtf=card)
            else:
                await message.reply(text="你的地址是不是输错了喵╭(●｀∇´●)╮？")
                
        except Exception as e:
            await message.reply(text=f"查询失败：{str(e)}")
    
    async def get_server_status(self, server_address):
        """调用UAPI获取服务器状态"""
        params = {"server": server_address}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    return None
                else:
                    raise Exception(f"API返回错误：{response.status}")
    
    async def create_status_card(self, status_info):
        """创建状态卡片"""
        motd = status_info.get("motd_clean", "")
        players = status_info.get("players", 0)
        max_players = status_info.get("max_players", 0)
        version = status_info.get("version", "")
        favicon = status_info.get("favicon", "")
        
        # 构建消息链
        message_parts = []
        
        # 添加服务器图标（如果有）
        if favicon:
            try:
                # 处理base64图片
                icon_data = favicon.split(",")[1] if "," in favicon else favicon
                image_data = base64.b64decode(icon_data)
                
                # 创建PIL Image对象
                img = PILImage.open(BytesIO(image_data))
                
                # 调整大小
                img = img.resize((64, 64), PILImage.Resampling.LANCZOS)
                
                # 转换回base64
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                message_parts.append(Image(f"base64://{img_base64}"))
            except:
                pass
        
        # 添加状态标题
        status = "✅ 在线" if status_info.get("online", False) else "❌ 离线"
        message_parts.append(Text(f"【Minecraft服务器状态】\n"))
        message_parts.append(Text(f"状态: {status}\n"))
        message_parts.append(Text(f"描述: {motd}\n"))
        message_parts.append(Text(f"玩家: {players}/{max_players} \n"))
        
        if version:
            message_parts.append(Text(f"版本: {version}\n"))
        
        
        return MessageChain(message_parts)
