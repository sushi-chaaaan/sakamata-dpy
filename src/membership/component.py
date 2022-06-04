import discord
from discord import ui

from model.system_text import ErrorText
from tools.logger import getMyLogger


class Start_Verify_View(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.logger = getMyLogger(__name__)

    @ui.button(
        label="認証を始める",
        style=discord.ButtonStyle.gray,
        emoji="\N{Envelope with Downwards Arrow Above}",
    )
    async def start_verify(self, interaction: discord.Interaction, button: ui.Button):
        # response
        await interaction.response.defer(ephemeral=True)
        self.logger.info(
            "{user} used start_verify button".format(user=str(interaction.user))
        )

        # start verify
        await interaction.followup.send()

        # send DM
        try:
            await interaction.user.send()
        except discord.Forbidden as e:
            self.logger.exception(
                f"Failed to send DM to {interaction.user}", exc_info=e
            )
            await interaction.followup.send(content=ErrorText.failed_to_dm.value)
        except Exception as e:
            self.logger.error(
                f"Failed to send DM to {str(interaction.user)}", exc_info=e
            )
