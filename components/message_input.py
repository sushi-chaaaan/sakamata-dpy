import discord
from discord import ui

from src.exts.modal_tracker import InteractionModalTracker

from .modal_tracker import MessageInput
from .view_handler import to_unavailable


class MessageInputView(ui.View):
    def __init__(self, custom_id: str):
        super().__init__(timeout=None)
        global c_id
        c_id = custom_id

    @ui.button(label="メッセージ入力(input)", style=discord.ButtonStyle.blurple)
    async def input_button(self, interaction: discord.Interaction, button: ui.Button):

        # get input
        modal: MessageInput = MessageInput(
            title="メッセージ入力",
            timeout=None,
            custom_id=c_id + "message_input_view",
            min_length=1,
            max_length=2000,
        )

        tracker = InteractionModalTracker(interaction)

        pass

    @ui.button(label="実行(start)", style=discord.ButtonStyle.success)
    async def exe_button(self, interaction: discord.Interaction, button: ui.Button):
        pass

    @ui.button(label="キャンセル(cancel)", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction: discord.Interaction, button: ui.Button):

        # ignore if there is no message
        if not interaction.message:
            return

        # disable view
        disabled_view: ui.View = to_unavailable(self)
        await interaction.message.edit(view=disabled_view)
        self.stop()
