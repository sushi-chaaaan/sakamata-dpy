import os

from discord import Interaction, app_commands, Object
from discord.ext import commands
from dotenv import load_dotenv

from src.bot import ChloeriumBot
from tools.log_formatter import command_log
from tools.logger import getMyLogger


class Reload(commands.Cog):
    def __init__(self, bot: ChloeriumBot):
        self.bot = bot
        load_dotenv()
        self.logger = getMyLogger(__name__)

    @app_commands.command(name="reload")
    @app_commands.guilds(Object(id=int(os.environ["GUILD_ID"])))
    async def reload(self, interaction: Interaction) -> None:
        # admin only

        """Botを落とすことなく機能を再読み込みします。"""

        self.logger.info(command_log(name="reload", author=interaction.user))
        await interaction.response.defer(ephemeral=True)

        await self.bot.reload_exts()

        await interaction.followup.send("All extensions reloaded", ephemeral=True)
        return


async def setup(bot: ChloeriumBot):
    await bot.add_cog(Reload(bot))
