import discord
from discord import ui

from model.tracked_modal import TrackedModal
from src.exts.modal_tracker import InteractionModalTracker

from .modal_tracker import MessageInputModal
from .view_handler import to_unavailable

c_id = ""


class MessageInputView(ui.View):
    def __init__(self, custom_id: str):
        super().__init__(timeout=None)
        global c_id
        c_id = custom_id
        self.content: str | None = None
        self.status: bool = False

    @ui.button(
        label="入力(input)", style=discord.ButtonStyle.blurple, custom_id=c_id + "_input"
    )
    async def input_button(self, interaction: discord.Interaction, button: ui.Button):

        # get input
        inputs: list[ui.TextInput] = [
            ui.TextInput(
                label="送信するメッセージを入力してください。",
                style=discord.TextStyle.paragraph,
                max_length=2000,
                required=True,
            )
        ]

        modal: MessageInputModal = MessageInputModal(
            title="メッセージ入力",
            timeout=None,
            custom_id=c_id + "message_input_view",
            inputs=inputs,
        )

        # send modal and wait
        tracker = InteractionModalTracker(modal, interaction=interaction)
        tracked: TrackedModal = await tracker.track(direct=True, ephemeral=True)

        # set content
        self.content = tracked.text_inputs["送信するメッセージを入力してください。"]

        # edit preview
        if (m := interaction.message) and m.embeds:
            m.embeds[0].description = self.content
            await m.edit(embeds=m.embeds)

        await interaction.followup.send("メッセージを入力しました。", ephemeral=True)
        return

    @ui.button(
        label="実行(start)", style=discord.ButtonStyle.success, custom_id=c_id + "_start"
    )
    async def exe_button(self, interaction: discord.Interaction, button: ui.Button):
        # defer
        await interaction.response.defer(thinking=True)

        # ignore if there is no content

        if self.content is None:
            await interaction.followup.send("送信するメッセージが入力されていません。")
            return

        # send message
        if m := interaction.message:
            await m.edit(view=to_unavailable(self))

        await interaction.followup.send("send message triggered.")
        self.status = True
        self.stop()

    @ui.button(
        label="キャンセル(cancel)",
        style=discord.ButtonStyle.danger,
        custom_id=c_id + "_cancel",
    )
    async def cancel_button(self, interaction: discord.Interaction, button: ui.Button):

        # disable view
        await interaction.response.defer(ephemeral=True)
        if m := interaction.message:
            await m.edit(view=to_unavailable(self))

        # cancel
        await interaction.followup.send("実行を停止します。", ephemeral=True)
        self.status = False
        self.stop()
