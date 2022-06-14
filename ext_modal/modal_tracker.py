import discord
from discord import Interaction, InteractionResponded, ui

from ext_modal.components.modal import ModalView
from ext_modal.model.tracked_modal import TrackedModal
from model.exception import InteractionExpired


class InteractionModalTracker:
    def __init__(self, modal: ui.Modal, *, interaction: Interaction) -> None:
        self.__modal = modal
        self.__interaction = interaction

    async def track(
        self,
        *,
        ephemeral: bool = False,
        direct: bool = False,
    ) -> TrackedModal:

        # interaction is expired
        if self.__interaction.is_expired():
            if (
                not ephemeral
                and not direct
                and isinstance(
                    ch := self.__interaction.channel, discord.abc.Messageable
                )
            ):
                view = ModalView(self.__interaction, modal=self.__modal, timeout=None)
                await ch.send(
                    view=ModalView(self.__interaction, modal=self.__modal, timeout=None)
                )
                await view.wait()
                return TrackedModal(view.__modal)

            # cannot send as normal message
            raise InteractionExpired()

        # interaction is available

        if not direct:
            view = ModalView(self.__interaction, modal=self.__modal, timeout=None)
            if self.__interaction.response.is_done():
                await self.__interaction.followup.send(view=view, ephemeral=ephemeral)
            else:
                await self.__interaction.response.send_message(
                    view=view, ephemeral=ephemeral
                )
            await view.wait()
            return TrackedModal(self.__modal)

        # cannot send modal
        if self.__interaction.response.is_done():
            await self.__interaction.followup.send("フォームを送信できません。", ephemeral=ephemeral)
            raise InteractionResponded(self.__interaction)

        # send modal directly and track it
        await self.__interaction.response.send_modal(self.__modal)
        await self.__modal.wait()
        return TrackedModal(self.__modal)
