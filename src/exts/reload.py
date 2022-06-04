from discord.ext import commands
from dotenv import load_dotenv
from src.bot import ChloeriumBot


class Reload(commands.Cog):
    def __init__(self, bot: ChloeriumBot):
        self.bot = bot
        load_dotenv()

    @commands.command(name="reload")
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx: commands.Context):
        await self.bot.reload_exts()
        await ctx.reply("Reloaded!!!")


async def setup(bot: ChloeriumBot):
    await bot.add_cog(Reload(bot))
