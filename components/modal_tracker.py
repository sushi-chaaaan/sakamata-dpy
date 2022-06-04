import discord
from discord import Interaction, InteractionResponded, ui

from model.exception import InteractionExpired


class InteractionModalTracker:
    def __init__(self, modal: ui.Modal, *, interaction: Interaction) -> None:
        self._modal = modal
        self._interaction = interaction

    async def track(
        self,
        *,
        ephemeral: bool = False,
        direct: bool = False,
    ) -> dict[str, str | None]:

        if self._interaction.is_expired():
            raise InteractionExpired()

        if not direct:
            # send modal via view
            view = ModalView(self._interaction, modal=self._modal, timeout=None)

            if self._interaction.response.is_done():
                await self._interaction.followup.send(view=view, ephemeral=ephemeral)
            else:
                await self._interaction.response.send_message(
                    view=view, ephemeral=ephemeral
                )
            await view.wait()
            return value_to_dict(view._modal)

        else:
            # send modal directly
            if self._interaction.response.is_done():
                await self._interaction.followup.send(
                    "フォームを送信できません。", ephemeral=ephemeral
                )
                raise InteractionResponded(self._interaction)
            else:
                await self._interaction.response.send_modal(self._modal)
                await self._modal.wait()
                return value_to_dict(self._modal)


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
        self.origin_interaction = origin_interaction
        self.value: dict[str, str | None] = {}

    @ui.button(
        label="入力",
        custom_id="message_input_button",
        style=discord.ButtonStyle.blurple,
        emoji="\N{Pencil}",
        row=0,
    )
    async def input_button(self, interaction: Interaction, button: ui.Button):

        # disable view
        view = to_unavailable(self)
        if not self.origin_interaction or self.origin_interaction.is_expired():
            if not interaction.message:
                pass
            else:
                await interaction.message.edit(view=view)
        else:
            await self.origin_interaction.edit_original_message(view=view)

        # send modal and wait
        await interaction.response.send_modal(self._modal)
        await self._modal.wait()
        self.stop()


def to_unavailable(view: ui.View) -> ui.View:
    for c in view.children:
        if isinstance(c, ui.Button) or isinstance(c, ui.Select):
            c.disabled = True
        else:
            pass
    return view


def value_to_dict(modal: ui.Modal) -> dict[str, str | None]:
    d: dict[str, str | None] = {}
    for item in modal.children:
        if not isinstance(item, ui.TextInput):
            continue
        else:
            d[item.label] = item.value
    return d


class MessageInput(ui.Modal):
    def __init__(
        self,
        *,
        title: str,
        timeout: float | None = None,
        custom_id: str,
        min_length: int,
        max_length: int,
    ) -> None:
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
        self.input: ui.TextInput = ui.TextInput(
            label="入力フォーム",
            style=discord.TextStyle.paragraph,
            placeholder="メッセージを入力",
            min_length=min_length,
            max_length=max_length,
        )
        self.add_item(self.input)

    async def on_submit(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        self.stop()
