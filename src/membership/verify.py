import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from components.confirm import ConfirmView
from tools.checker import Checker
from tools.finder import Finder

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
        # client = GSheetClient(os.environ["SPREAD_SHEET_CRED"])
        pass

    @commands.command(name="verify")
    @commands.dm_only()
    async def verify(
        self, ctx: commands.Context, attachment: discord.Attachment | None = None
    ):

        # check attachment
        checker = Checker(self.bot)
        if not attachment or not checker.check_content_type(
            attachment, ["image/png", "image/jpeg"]
        ):
            await ctx.reply("画像を添付してください。")
            return

        # do confirm
        res = await self.do_confirm(attachment.url)

        text = "verified" if res else "rejected"
        await ctx.reply(f"{text}")
        return

    async def do_confirm(self, image_url: str) -> bool:

        # generate confirmation message
        view = ConfirmView(
            custom_id="exts.membership.verify.do_confirm",
            timeout=None,
        )

        embed = EB.member_confirm_embed(image_url)

        # do confirm
        finder = Finder(self.bot)
        channel = await finder.search_channel(int(os.environ["MEMBERSHIP_CHANNEL"]))

        if not isinstance(channel, discord.TextChannel | discord.Thread):
            raise Exception("Failed to get MessageableChannel")

        await channel.send(embeds=[embed], view=view)
        await view.wait()
        return view.value


async def setup(bot: commands.Bot):
    await bot.add_cog(MemberShip(bot))
