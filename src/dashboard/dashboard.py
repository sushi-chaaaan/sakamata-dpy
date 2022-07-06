import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from src.bot import ChloeriumBot
from tools.log_formatter import command_log
from tools.logger import getMyLogger

from .components import DashBoardPanel


class DashBoard(commands.Cog):
    def __init__(self, bot: ChloeriumBot):
        # init cog
        self.bot = bot
        load_dotenv()

        # init logger
        self.logger = getMyLogger(__name__)

    @app_commands.command(name="dashboard")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    async def dashboard(self, interaction: discord.Interaction):
        """機能の一括管理を行えるダッシュボードを呼び出します。"""
        # defer and log
        await interaction.response.defer(ephemeral=True)
        self.logger.info(command_log(name="dashboard", author=interaction.user))

        # send dashboard
        await interaction.followup.send(view=DashBoardPanel(self.bot))


async def setup(bot: ChloeriumBot):
    await bot.add_cog(DashBoard(bot))
