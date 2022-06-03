import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from tools.gsheets import GSheetClient


class MemberShip(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()

    @commands.command(name="send-membership")
    @commands.guild_only()
    @commands.has_role(int(os.environ["ADMIN"]))
    async def send_membership(self, ctx: commands.Context, *, msg: str):
        await ctx.send(msg)

    async def post_to_sheet(self):
        client = GSheetClient(os.environ["SPREAD_SHEET_CRED"])


async def setup(bot: commands.Bot):
    await bot.add_cog(MemberShip(bot))
