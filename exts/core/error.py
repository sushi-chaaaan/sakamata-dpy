from discord.ext import commands
from dotenv import load_dotenv

from tools.logger import getMyLogger

logger = getMyLogger(__name__)


class ErrorCatcher(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()

    @commands.Cog.listener(name="on_error")
    async def on_error(self, *args, **kwargs):
        logger.error(f"{args}\n\n{kwargs}")
        return

    @commands.Cog.listener(name="on_command_error")
    async def _on_command_error(self, ctx: commands.Context, exc: Exception):
        name = None if not ctx.command else ctx.command.name
        logger.error(
            f"on_command_error: \n{ctx.author} used {name} command", exc_info=exc
        )
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(ErrorCatcher(bot))
