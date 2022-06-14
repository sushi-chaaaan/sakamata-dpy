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
        # init cog
        self.bot = bot
        load_dotenv()

        # init logger
        self.logger = getMyLogger(__name__)

    @app_commands.command(name="dakuten")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(text="濁点をつける文章を入力")
    @app_commands.rename(text="濁点をつける文章")
    async def dakuten(self, interaction: discord.Interaction, text: str):
        """濁点を付けるだけのコマンド"""
        # defer and log
        await interaction.response.defer(ephemeral=True)
        self.logger.info(command_log(name="dakuten", author=interaction.user))

        # dakuten
        out_text = "".join([text[num] + "゛" for num in range(len(text))])

        # command response
        await interaction.followup.send(out_text, ephemeral=True)
        return

    @app_commands.command(name="timestamp")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(date="日付を入力してください。(例: 20220101→2021年1月1日)")
    @app_commands.describe(time="時間を24時間表記で入力してください。(例: 1200→昼の12時")
    @app_commands.rename(date="日付")
    @app_commands.rename(time="時間")
    async def timestamp(
        self,
        interaction: discord.Interaction,
        date: str = "20220101",
        time: str = "1200",
    ):
        """日付をDiscordで使用できるタイムスタンプに変換します。"""
        # defer and log
        await interaction.response.defer(ephemeral=True)
        self.logger.info(command_log(name="timestamp", author=interaction.user))

        # get date
        _date = datetime.strptime(date, "%Y%m%d")
        _date.replace(tzinfo=JST())

        # get hour
        delta = timedelta(hours=int(time[0:2]), minutes=int(time[2:4]))

        # get timestamp
        _dt = _date + delta
        timestamp = discord.utils.format_dt(_dt.astimezone(timezone.utc), style="f")

        # command response
        await interaction.followup.send(timestamp, ephemeral=True)
        await interaction.followup.send(f"```{timestamp}```", ephemeral=True)
        return

    @commands.hybrid_command(name="ping")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    async def ping(self, ctx: commands.Context):
        """ping!pong!"""
        # defer and log
        await ctx.defer(ephemeral=True)
        self.logger.info(command_log(name="ping", author=ctx.author))

        # command response
        await ctx.send(
            content=f"pong!\nping is {self.bot.latency * 1000:.2f}ms", ephemeral=True
        )
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(Utils(bot))
