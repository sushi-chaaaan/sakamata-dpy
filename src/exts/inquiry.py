import os

import discord
from discord import app_commands, ui
from discord.ext import commands
from dotenv import load_dotenv

from components.modal_tracker import MessageInputModal
from model.tracked_modal import TrackedModal
from tools.log_formatter import command_log
from tools.logger import getMyLogger
from tools.webhook import post_webhook

from .embeds import EmbedBuilder as EB
from .modal_tracker import InteractionModalTracker


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
        view = InquiryView(timeout=None)

        # send
        await channel.send(embeds=[embed], view=view)

        await interaction.followup.send(f"{channel.mention}に問い合わせフォームを送信しました。")
        return


class InquiryView(ui.View):
    def __init__(self, *, timeout: float | None = None):
        super().__init__(timeout=timeout)
        self.logger = getMyLogger(__name__)

    @ui.button(
        label="お問い合わせ",
        custom_id="exts.core.inquiry.inquiry_view",
        style=discord.ButtonStyle.gray,
        emoji="\N{Pencil}",
        row=0,
    )
    async def inquiry_button(
        self, interaction: discord.Interaction, button: ui.Button
    ) -> None:

        # get context
        modal = MessageInputModal(
            title="お問い合わせ内容を入力してください。",
            custom_id="exts.core.inquiry.inquiry_button",
            min_length=1,
            max_length=2000,
            label="入力フォーム",
        )

        tracker = InteractionModalTracker(modal, interaction=interaction)

        # get text input
        tracked: TrackedModal = await tracker.track(ephemeral=True, direct=True)
        if not (text := tracked.text_inputs["入力フォーム"]):
            return

        embed = EB.inquiry_view_embed(value=text, target=interaction.user)

        res = await post_webhook(os.environ["INQUIRY_WEBHOOK_URL"], embeds=[embed])
        if res.succeeded:
            await interaction.followup.send("お問い合わせを送信しました。", ephemeral=True)
            return
        self.logger.error(
            f"Failed to send inquiry.\nPosted by:{interaction.user.mention}(ID: {interaction.user.id})\nException: {str(res.exception)}"
        )
        await interaction.followup.send(
            "お問い合わせの送信に失敗しました。\n管理者による対応をお待ちください。", ephemeral=True
        )
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(Inquiry(bot))
