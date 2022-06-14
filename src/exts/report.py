import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from ext_modal.components.modal import MessageInputModal
from ext_modal.modal_tracker import InteractionModalTracker
from ext_modal.model.tracked_modal import TrackedModal
from tools.log_formatter import command_log
from tools.logger import getMyLogger


class Report(commands.Cog):
    def __init__(self, bot: commands.Bot):
        # init cog
        self.bot = bot
        load_dotenv()

        # init logger
        self.logger = getMyLogger(__name__)

        # init context menu
        self.user_ctx_menu_report = app_commands.ContextMenu(
            name="report",
            callback=self.report_user,
            guild_ids=[int(os.environ["GUILD_ID"])],
        )
        self.message_ctx_menu_report = app_commands.ContextMenu(
            name="report",
            callback=self.report_message,
            guild_ids=[int(os.environ["GUILD_ID"])],
        )
        self.bot.tree.add_command(self.user_ctx_menu_report)
        self.bot.tree.add_command(self.message_ctx_menu_report)

    async def cog_unload(self) -> None:
        # remove context menu
        self.bot.tree.remove_command(
            self.user_ctx_menu_report.name,
            type=self.user_ctx_menu_report.type,
        )
        self.bot.tree.remove_command(
            self.message_ctx_menu_report.name,
            type=self.message_ctx_menu_report.type,
        )

    @app_commands.guild_only()
    async def report_user(
        self, interaction: discord.Interaction, user: discord.Member
    ) -> None:
        # log
        self.logger.info(command_log(name="report_user", author=ctx.author))

        # get context
        ctx = await commands.Context.from_interaction(interaction)

        modal = MessageInputModal(
            title=f"{user}を管理者に通報しますか？",
            custom_id="exts.core.report.report_user",
            min_length=1,
            max_length=2000,
        )

        tracker = InteractionModalTracker(modal, interaction=interaction)

        # get text input
        tracked: TrackedModal = await tracker.track(ephemeral=True, direct=True)
        if not (text := tracked.text_inputs["入力フォーム"]):
            await ctx.send(content="正しく入力されませんでした。")
            return

        await ctx.send(f"{user}を管理者に通報しました。", ephemeral=True)
        return

    @app_commands.guild_only()
    async def report_message(
        self, interaction: discord.Interaction, message: discord.Message
    ) -> None:

        # log
        self.logger.info(command_log(
            name="report_message", author=interaction.user))

        # get context
        ctx = await commands.Context.from_interaction(interaction)

        modal = MessageInputModal(
            title="選択したメッセージを管理者に通報しますか？",
            custom_id="exts.core.report.report_message",
            min_length=1,
            max_length=2000,
        )

        tracker = InteractionModalTracker(modal, interaction=interaction)

        # get text input
        tracked: TrackedModal = await tracker.track(ephemeral=True, direct=True)
        if not (text := tracked.text_inputs["入力フォーム"]):
            await ctx.send(content="正しく入力されませんでした。")
            return

        await ctx.send("メッセージを管理者に通報しました。", ephemeral=True)
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(Report(bot))
