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

    @ui.button(label="メッセージ入力(input)", style=discord.ButtonStyle.blurple)
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
        await interaction.followup.send("メッセージを入力しました。", ephemeral=True)
        return

    @ui.button(label="実行(start)", style=discord.ButtonStyle.success)
    async def exe_button(self, interaction: discord.Interaction, button: ui.Button):
        pass

    @ui.button(label="キャンセル(cancel)", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction: discord.Interaction, button: ui.Button):

        # ignore if there is no message
        if not interaction.message:
            return

        # disable view
        await interaction.response.defer(ephemeral=True)
        disabled_view: ui.View = to_unavailable(self)
        await interaction.message.edit(view=disabled_view)
        await interaction.followup.send("実行を停止します。", ephemeral=True)
        self.stop()
