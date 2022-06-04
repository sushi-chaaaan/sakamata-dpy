from discord.ext import commands

from src.bot import ChloeriumBot
from tools.log_formatter import command_log
from tools.logger import getMyLogger


class Reload(commands.Cog):
    def __init__(self, bot: ChloeriumBot):
        self.bot = bot
        self.logger = getMyLogger(__name__)

    @commands.command(name="reload")
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx: commands.Context):
        self.logger.info(command_log(name="reload", author=ctx.author))

        await self.bot.reload_exts()
        await ctx.reply("Reloaded!!!")
        return


async def setup(bot: ChloeriumBot):
    await bot.add_cog(Reload(bot))
