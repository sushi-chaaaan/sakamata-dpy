import os

import discord
from discord import ui
from dotenv import load_dotenv

from ext_modal.components.message_input import MessageInputModal
from ext_modal.modal_tracker import InteractionModalTracker
from ext_modal.model.tracked_modal import TrackedModal
from tools.logger import getMyLogger
from tools.webhook import post_webhook

from .embeds import EmbedBuilder as EB


class InquiryView(ui.View):
    custom_id = "src.exts.inquiry.InquiryView"

    def __init__(self, *, custom_id: str, timeout: float | None = None):
        super().__init__(timeout=timeout)
        load_dotenv()
        self.logger = getMyLogger(__name__)
        self.status: bool = False
        self.content: str | None = None

    @ui.button(
        label="お問い合わせ",
        custom_id=custom_id,
        style=discord.ButtonStyle.gray,
        emoji="\N{Pencil}",
        row=0,
    )
    async def inquiry_button(
        self, interaction: discord.Interaction, button: ui.Button
    ) -> None:

        # get text

        inputs: list[ui.TextInput] = [
            ui.TextInput(
                label="お問い合わせ内容を入力してください。",
                style=discord.TextStyle.paragraph,
            )
        ]
        modal: MessageInputModal = MessageInputModal(
            title="お問い合わせフォーム",
            timeout=None,
            custom_id="components.inquiry.InquiryView.inquiry_button",
            inputs=inputs,
        )

        tracker = InteractionModalTracker(modal, interaction=interaction)
        tracked: TrackedModal = await tracker.track(direct=True, ephemeral=True)

        if not (text := tracked.text_inputs["お問い合わせ内容を入力してください。"]):
            return

        # send webhook
        embed = EB.inquiry_view_embed(value=text, target=interaction.user)
        res = await post_webhook(os.environ["INQUIRY_WEBHOOK_URL"], embeds=[embed])

        # success
        if res.succeeded:
            await interaction.followup.send("お問い合わせを送信しました。", ephemeral=True)
            return

        # failed
        self.logger.error(
            f"Failed to send inquiry.\nPosted by:{interaction.user.mention}(ID: {interaction.user.id})\nException: {str(res.exception)}"
        )
        await interaction.followup.send(
            "お問い合わせの送信に失敗しました。\n管理者による対応をお待ちください。", ephemeral=True
        )
        return
