import os

from discord import Interaction, Object, app_commands
from discord.ext import commands
from dotenv import load_dotenv

from src.bot import ChloeriumBot
from tools.log_formatter import command_log
from tools.logger import getMyLogger


class Reload(commands.Cog):
    def __init__(self, bot: ChloeriumBot):
        # init cog
        self.bot = bot
        load_dotenv()

        # init logger
        self.logger = getMyLogger(__name__)

    @app_commands.command(name="reload")
    @app_commands.guilds(Object(id=int(os.environ["GUILD_ID"])))
    async def reload(self, interaction: Interaction) -> None:
        # admin only
        """Botを落とすことなく機能を再読み込みします。"""
        # defer and log
        await interaction.response.defer(ephemeral=True)
        self.logger.info(command_log(name="reload", author=interaction.user))

        # reload
        await self.bot.load_exts(reload=True)

        # command response
        await interaction.followup.send("All extensions reloaded", ephemeral=True)
        return


async def setup(bot: ChloeriumBot):
    await bot.add_cog(Reload(bot))
