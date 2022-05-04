import os

import discord
from discord.ext import commands
from dotenv import load_dotenv


class Confirm(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()

    async def confirm(
        self, ctx: commands.Context, target: discord.abc.Snowflake
    ) -> bool:
        pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Confirm(bot))
