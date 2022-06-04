import discord
from discord import Interaction, InteractionResponded, ui

from components.modal_tracker import ModalView
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

            # check if it is allowed to send as normal message
            if not ephemeral and not direct:

                # check channel
                if not isinstance(
                    ch := self._interaction.channel, discord.abc.Messageable
                ):
                    raise InteractionExpired()

                # send as normal message

                view = ModalView(self._interaction, modal=self._modal, timeout=None)

                await ch.send(
                    view=ModalView(self._interaction, modal=self._modal, timeout=None)
                )
                await view.wait()
                return value_to_dict(view._modal)

            else:
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

    async def _track(self, view: ModalView) -> dict[str, str | None]:
        await view.wait()
        return value_to_dict(view._modal)


def value_to_dict(modal: ui.Modal) -> dict[str, str | None]:
    d: dict[str, str | None] = {}
    for item in modal.children:
        if not isinstance(item, ui.TextInput):
            continue
        else:
            d[item.label] = item.value
    return d
