import discord
from discord import Interaction, InteractionResponded, ui

from components.modal_tracker import ModalView
from model.exception import InteractionExpired
from model.tracked_modal import TrackedModal


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

        if self.__interaction.is_expired():

            # check if it is allowed to send as normal message
            if not ephemeral and not direct:

                # check channel
                if not isinstance(
                    ch := self.__interaction.channel, discord.abc.Messageable
                ):
                    raise InteractionExpired()

                # send as normal message
                view = ModalView(self.__interaction, modal=self.__modal, timeout=None)

                await ch.send(
                    view=ModalView(self.__interaction, modal=self.__modal, timeout=None)
                )
                await view.wait()
                return TrackedModal(view.__modal)

            else:
                raise InteractionExpired()

        if not direct:
            # send modal via view
            view = ModalView(self.__interaction, modal=self.__modal, timeout=None)

            if self.__interaction.response.is_done():
                await self.__interaction.followup.send(view=view, ephemeral=ephemeral)
            else:
                await self.__interaction.response.send_message(
                    view=view, ephemeral=ephemeral
                )
            await view.wait()
            return TrackedModal(self.__modal)

        else:
            # send modal directly
            if self.__interaction.response.is_done():
                await self.__interaction.followup.send(
                    "フォームを送信できません。", ephemeral=ephemeral
                )
                raise InteractionResponded(self.__interaction)
            else:
                await self.__interaction.response.send_modal(self.__modal)
                await self.__modal.wait()
                return TrackedModal(self.__modal)
