from discord import ButtonStyle, Interaction, TextStyle, ui

from .view_handler import to_unavailable


class ModalView(ui.View):
    def __init__(
        self,
        origin_interaction: Interaction,
        *,
        modal: ui.Modal,
        timeout: float | None = None,
    ):
        super().__init__(timeout=timeout)
        self._modal = modal
        self._interaction = origin_interaction

    @ui.button(
        label="入力",
        custom_id="message_input_button",
        style=ButtonStyle.gray,
        emoji="\N{Pencil}",
        row=0,
    )
    async def input_button(self, interaction: Interaction, button: ui.Button):

        # disable view
        view = to_unavailable(self)
        if not self._interaction or self._interaction.is_expired():
            if not interaction.message:
                pass
            else:
                await interaction.message.edit(view=view)
        else:
            await self._interaction.edit_original_message(view=view)

        # send modal and wait
        await interaction.response.send_modal(self._modal)
        await self._modal.wait()
        self.stop()


class MessageInput(ui.Modal):
    def __init__(
        self,
        *,
        title: str,
        timeout: float | None = None,
        custom_id: str,
        min_length: int,
        max_length: int,
        label: str = "入力フォーム",
    ) -> None:
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        self.input: ui.TextInput = ui.TextInput(
            label=label,
            style=TextStyle.paragraph,
            placeholder="メッセージを入力",
            min_length=min_length,
            max_length=max_length,
        )
        self.add_item(self.input)

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        self.stop()
