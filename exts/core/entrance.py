import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from tools.dt import dt_to_str
from tools.logger import getMyLogger

logger = getMyLogger(__name__)


class Entrance(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()
        self.entrance_channel = int(os.environ["ENTRANCE_CHANNEL"])

    @commands.Cog.listener(name="on_member_join")
    async def on_join(self, member: discord.Member):
        status = "参加"
        await self.send_member_log(member, status)
        return

    @commands.Cog.listener(name="on_member_remove")
    async def on_leave(self, member: discord.Member):
        status = "退出"
        await self.send_member_log(member, status)
        return

    async def send_member_log(self, member: discord.Member, status):
        channel = self.bot.get_channel(self.entrance_channel)
        if not channel:
            channel = await self.bot.fetch_channel(self.entrance_channel)
        if not isinstance(channel, discord.abc.Messageable):
            logger.error("Failed to get Messageable channel")
            return
        send_msg = f"時刻: {dt_to_str()}\n{status}メンバー名: {member.name} (ID:{member.id})\nメンション: {member.mention}\nアカウント作成時刻: {dt_to_str(member.created_at)}\n現在のメンバー数:{member.guild.member_count}\n"
        await channel.send(send_msg)
        return


async def setup(bot):
    await bot.add_cog(Entrance(bot))
