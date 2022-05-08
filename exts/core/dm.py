import os

import discord
from components.text_input import TextInputTracker
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from tools.confirm import Checker
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
        logger.info(
            f"{interaction.user}[ID: {interaction.user.id}] used send-dm command"
        )
        await interaction.response.defer(thinking=True)
        ctx = await commands.Context.from_interaction(interaction)
        tracker = TextInputTracker(ctx)
        value = await tracker.track_modal(
            title="DM内容入力",
            custom_id="exts.core.dm.send_dm_track_modal",
            min_length=1,
            max_length=2000,
            timeout=None,
        )
        if not value:
            await ctx.send(content="実行をキャンセルします。")
            return

        # confirm
        role = ctx.guild.get_role(int(os.environ["ADMIN"]))  # type: ignore -> checked by Discord server side
        if not role:
            return
        check = Checker(self.bot)
        header = (
            f"{target.mention}へ次のダイレクトメッセージを送信します。"
            if not attachment
            else f"{target.mention}へ次のダイレクトメッセージを送信します。\n添付ファイルの数は1件です。"
        )
        res = await check.check_role(
            ctx=ctx,
            watch_role=role,
            header=header,
            text=value,
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
                await target.send(content=value, file=await attachment.to_file())
            else:
                await target.send(content=value)
        except Exception as e:
            logger.exception(f"Failed to send DM to {target}", exc_info=e)
            await ctx.send(content="DM送信に失敗しました。\n対象がDMを受け取らない設定になっている可能性があります。")
            return
        else:
            logger.info(f"DM was sent to {target}")
            await ctx.send(content="DM送信に成功しました。")
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(DMSys(bot))
