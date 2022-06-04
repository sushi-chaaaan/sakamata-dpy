import os
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from tools.dt import JST
from tools.log_formatter import command_log
from tools.logger import getMyLogger


class Utils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()
        self.logger = getMyLogger(__name__)

    @app_commands.command(name="dakuten")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(text="text to add dakuten")
    async def dakuten(self, interaction: discord.Interaction, text: str):
        """濁点を付けて自慢しよう！"""

        self.logger.info(command_log(name="dakuten", author=interaction.user))

        await interaction.response.defer(ephemeral=True)
        out_text = "".join([text[num] + "゛" for num in range(len(text))])
        await interaction.followup.send(out_text, ephemeral=True)
        return

    @app_commands.command(name="timestamp")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(date="choose date to make timestamp. default is 20220101")
    @app_commands.describe(time="choose time to make timestamp. default is 1200")
    async def timestamp(
        self,
        interaction: discord.Interaction,
        date: str = "20220101",
        time: str = "1200",
    ):
        """日付をDiscordで使用できるタイムスタンプに変換します。"""

        self.logger.info(command_log(name="timestamp", author=interaction.user))

        await interaction.response.defer(ephemeral=True)
        _date = datetime.strptime(date, "%Y%m%d")
        _date.replace(tzinfo=JST())
        delta = timedelta(hours=int(time[0:2]), minutes=int(time[2:4]))
        _dt = _date + delta
        timestamp = discord.utils.format_dt(_dt.astimezone(timezone.utc), style="f")
        await interaction.followup.send(timestamp, ephemeral=True)
        await interaction.followup.send(f"```{timestamp}```", ephemeral=True)
        return

    @commands.hybrid_command(name="ping")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    async def ping(self, ctx: commands.Context):

        self.logger.info(command_log(name="ping", author=ctx.author))

        await ctx.send(content=f"pong!\nping is {self.bot.latency * 1000:.2f}ms")
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(Utils(bot))
