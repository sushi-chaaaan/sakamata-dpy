import os

import discord
from components.confirm import ConfirmView
from discord.ext import commands
from dotenv import load_dotenv
from model.response import ExecuteResponse
from tools.gsheets import GSheetClient
from tools.webhook import post_webhook

from .embeds import EmbedBuilder as EB


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

    @commands.command(name="verify")
    @commands.dm_only()
    async def verify(self, ctx: commands.Context, attachment: discord.Attachment):

        # check attachment
        VALID_CONTENT_TYPE = ["image/png", "image/jpeg"]
        if attachment.content_type not in VALID_CONTENT_TYPE:
            await ctx.reply("画像を添付してください。")
            return

        # do confirm

    async def do_confirm(self, image_url: str) -> bool:

        # generate confirmation message
        view = ConfirmView(
            custom_id="exts.membership.verify.do_confirm",
            accept="承認",
            reject="拒否",
            timeout=None,
        )

        embed = EB.member_confirm_embed(image_url)

        # do confirm
        await post_webhook(os.environ["MEMBER_WEBHOOK_URL"], embeds=[embed], view=view)
        await view.wait()
        res = view.value

        # check result


async def setup(bot: commands.Bot):
    await bot.add_cog(MemberShip(bot))
