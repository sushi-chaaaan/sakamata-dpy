import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from components.inquiry import InquiryView
from tools.log_formatter import command_log
from tools.logger import getMyLogger

from .embeds import EmbedBuilder as EB


class Inquiry(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()
        self.logger = getMyLogger(__name__)

    @app_commands.command(name="send_inquiry")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(channel="お問い合わせフォームを送信するチャンネルかスレッドを選択してください。")
    @app_commands.rename(channel="チャンネル")
    async def send_inquiry(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel | discord.Thread,
    ):
        """お問い合わせフォームを送信します。"""

        await interaction.response.defer()

        self.logger.info(command_log(name="send_inquiry", author=interaction.user))

        # get embed
        embed = EB.inquiry_embed()

        # get view
        view = InquiryView(custom_id="src.exts.inquiry.InquiryView", timeout=None)

        # send
        await channel.send(embeds=[embed], view=view)

        await interaction.followup.send(f"{channel.mention}に問い合わせフォームを送信しました。")
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(Inquiry(bot))
