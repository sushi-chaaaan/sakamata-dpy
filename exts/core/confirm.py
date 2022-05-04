import os

import discord
from discord.ext import commands
from dotenv import load_dotenv


class Confirm(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()

    async def confirm(self,target:discord.abc.Snowflake):


async def setup(bot: commands.Bot):
    await bot.add_cog(Confirm(bot))
