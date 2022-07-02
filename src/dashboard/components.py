import discord
from discord import ui

from src.bot import ChloeriumBot
from src.exts.reload import Reload


class DashBoardPanel(ui.View):
    def __init__(self, bot: ChloeriumBot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="スローモード設定")
    async def toggle_slow_mode(
        self, interaction: discord.Interaction, button: ui.Button
    ):
        await interaction.followup.send("スローモードを切り替えました。")
        return

    @ui.button(label="スレッドの自動可否設定")
    async def toggle_thread_auto_lock(
        self, interaction: discord.Interaction, button: ui.Button
    ):
        await interaction.followup.send("スレッドの自動可否設定を切り替えました。")
        return

    @ui.button(label="Botのリロード")
    async def reload(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.followup.send("Botのリロードを開始します。")

        r = Reload(self.bot)
        await r.do_reload(interaction)

        await interaction.followup.send("Botをリロードしました。")
        return
