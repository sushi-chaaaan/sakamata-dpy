import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from ext_modal.components.modal import MessageInputModal
from ext_modal.modal_tracker import InteractionModalTracker
from ext_modal.model.tracked_modal import TrackedModal
from tools.checker import Checker
from tools.log_formatter import command_log
from tools.logger import getMyLogger


class DMSys(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()
        self.logger = getMyLogger(__name__)

    @app_commands.command(name="send-dm")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(target="DMを送信するユーザーを選択してください。")
    @app_commands.describe(attachment="添付するファイルがあれば添付してください。")
    @app_commands.rename(target="送り先")
    @app_commands.rename(attachment="添付ファイル")
    async def send_dm(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        attachment: discord.Attachment | None = None,
    ):
        """DMを送信します。"""
        # defer and log
        await interaction.response.defer(thinking=True)
        self.logger.info(command_log(name="send-dm", author=interaction.user))

        # get context
        ctx = await commands.Context.from_interaction(interaction)

        # get text input
        modal = MessageInputModal(
            title="DM内容入力",
            custom_id="exts.core.dm.send_dm_track_modal",
            min_length=1,
            max_length=2000,
            label="入力フォーム",
        )

        tracker = InteractionModalTracker(modal, interaction=interaction)
        tracked: TrackedModal = await tracker.track()
        if not (text := tracked.text_inputs["入力フォーム"]):
            await ctx.send(content="実行をキャンセルします。")
            return

        # confirm
        checker = Checker(self.bot)
        header = (
            f"{target.mention}へ次のダイレクトメッセージを送信します。"
            if not attachment
            else f"{target.mention}へ次のダイレクトメッセージを送信します。\n添付ファイルの数は1件です。"
        )
        res = await checker.check_role(
            ctx=ctx,
            id=int(os.environ["ADMIN"]),
            header=header,
            text=text,
            run_num=1,
            stop_num=1,
        )

        # cancel
        if not res:
            await ctx.send(content="実行をキャンセルします。")
            return

        # send
        await ctx.send(content="実行を開始します。")
        try:
            if attachment:
                await target.send(content=text, file=await attachment.to_file())
            else:
                await target.send(content=text)
        except Exception as e:
            self.logger.exception(f"Failed to send DM to {target}", exc_info=e)
            await ctx.send(content="DM送信に失敗しました。\n対象がDMを受け取らない設定になっている可能性があります。")
            return
        else:
            self.logger.info(f"DM was sent to {target}")
            await ctx.send(content="DM送信に成功しました。")
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(DMSys(bot))
