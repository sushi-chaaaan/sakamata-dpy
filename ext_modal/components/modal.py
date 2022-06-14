import discord
from discord import ButtonStyle, ui

from tools.view_handler import to_unavailable


class MessageInputModal(ui.Modal):
    def __init__(
        self,
        *,
        title: str,
        timeout: float | None = None,
        custom_id: str,
        inputs: list[ui.TextInput],
    ) -> None:
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        for f in inputs:
            self.add_item(f)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        self.stop()


# non-direct modeでModal起動用に送信されるView。Trackerから呼び出す前提
class ModalView(ui.View):
    def __init__(
        self,
        origin_interaction: discord.Interaction,
        *,
        modal: ui.Modal,
        timeout: float | None = None,
    ):
        super().__init__(timeout=timeout)
        self.__modal = modal
        self.__interaction = origin_interaction

    @ui.button(
        label="入力(input)",
        custom_id="ext_modal.components.modal.ModalView.input_button",
        style=ButtonStyle.blurple,
        row=0,
    )
    async def input_button(self, interaction: discord.Interaction, button: ui.Button):

        # disable view
        view = to_unavailable(self)
        if not self.__interaction or self.__interaction.is_expired():
            if not interaction.message:
                pass
            else:
                await interaction.message.edit(view=view)
        else:
            await self.__interaction.edit_original_message(view=view)

        # send modal and wait
        await interaction.response.send_modal(self.__modal)
        await self.__modal.wait()
        self.stop()