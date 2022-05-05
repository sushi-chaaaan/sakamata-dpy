import os

import discord
from components.text_input import TextInputTracker
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from tools.confirm import Confirm
from tools.logger import getMyLogger

logger = getMyLogger(__name__)


class DMSys(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()

    @app_commands.command(name="send-dm")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(target="Choose user to send DM")
    @app_commands.describe(attachment="File to send with message")
    async def send_dm(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        attachment: discord.Attachment | None = None,
    ):
        """ダイレクトメッセージの送信を行います。"""
        await interaction.response.defer(thinking=True)
        ctx = await commands.Context.from_interaction(interaction)
        tracker = TextInputTracker()
        value = await tracker.track_modal(
            ctx=ctx,
            title="DM内容入力",
            custom_id="exts.core.dm.send_dm_track_modal",
            min_length=1,
            max_length=2000,
            timeout=None,
        )
        if not value:
            await interaction.followup.send(content="実行をキャンセルします。")
            return

        # confirm
        role = ctx.guild.get_role(int(os.environ["ADMIN"]))  # type: ignore -> checked by Discord server side
        if not role:
            return
        check = Confirm(self.bot)
        header = (
            f"{target}へ次のダイレクトメッセージを送信します。"
            if not attachment
            else f"{target}へ次のダイレクトメッセージを送信します。\n添付ファイルの数は1件です。"
        )
        res = await check.confirm(
            ctx=ctx,
            watch_role=role,
            header=header,
            text=value,
            run_num=1,
            stop_num=1,
        )

        # cancel
        if not res:
            await interaction.followup.send(content="実行をキャンセルします。")
            return

        # send
        await interaction.followup.send(content="実行を開始します。")
        try:
            if attachment:
                await target.send(content=value, file=await attachment.to_file())
            else:
                await target.send(content=value)
        except Exception as e:
            logger.exception("Failed to send DM", exc_info=e)
            await interaction.followup.send(
                content="DM送信に失敗しました。\n対象がDMを受け取らない設定になっている可能性があります。"
            )
            return
        else:
            await interaction.followup.send(content="DM送信に成功しました。")
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(DMSys(bot))
