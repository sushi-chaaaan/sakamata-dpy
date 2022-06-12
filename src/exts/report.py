import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from components.modal_tracker import MessageInputModal
from model.tracked_modal import TrackedModal
from tools.log_formatter import command_log
from tools.logger import getMyLogger

from .modal_tracker import InteractionModalTracker


class Report(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()
        self.logger = getMyLogger(__name__)

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
        ctx = await commands.Context.from_interaction(interaction)

        self.logger.info(command_log(name="report_user", author=ctx.author))

        modal = MessageInput(
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
        ctx = await commands.Context.from_interaction(interaction)

        self.logger.info(command_log(name="report_message", author=ctx.author))

        modal = MessageInput(
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
