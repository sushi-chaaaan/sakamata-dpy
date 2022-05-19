import discord
from discord import Interaction, ui
from tools.logger import getMyLogger

logger = getMyLogger(__name__)


class ConfirmView(ui.View):
    def __init__(self, *, custom_id: str, timeout: float | None = None):
        super().__init__(timeout=timeout)
        global c_id
        c_id = custom_id

    @ui.button(
        label="承諾",
        custom_id=c_id + "_accept",
        style=discord.ButtonStyle.blurple,
        emoji="\N{White Heavy Check Mark}",
        row=0,
    )
    async def confirm_accept(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_message("承諾しました", ephemeral=True)
        self.value = True
        self.stop()

    @ui.button(
        label="拒否",
        custom_id=c_id + "_reject",
        style=discord.ButtonStyle.blurple,
        emoji="\N{Negative Squared Cross Mark}",
        row=1,
    )
    async def confirm_reject(self, interaction: Interaction, button: ui.Button):
        await interaction.response.send_message("拒否しました", ephemeral=True)
        self.value = False
        self.stop()
