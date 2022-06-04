import os

import discord
from components.text_input import TextInputTracker
from discord import app_commands
from discord.ext import commands
from dispander import dispand
from dotenv import load_dotenv
from tools.checker import Checker
from tools.logger import getMyLogger

from .messenger import Messenger


class MessageSys(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()
        self.logger = getMyLogger(__name__)

    @commands.Cog.listener("on_message")
    async def on_message_dispand(self, message: discord.Message):
        # ignore message not from Guild or Bot
        if (
            not isinstance(
                message.channel,
                discord.TextChannel | discord.VoiceChannel | discord.Thread,
            )
            or message.author.bot
        ):
            return

        # generate embed
        embeds = await dispand(self.bot, message)
        if not embeds:
            return

        # send embed
        await message.channel.send(embeds=embeds)
        return

    @app_commands.command(name="send-message")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(channel="Choose channel to send message")
    @app_commands.describe(attachment="File to send with message")
    async def send_message(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel | discord.VoiceChannel | discord.Thread,
        attachment: discord.Attachment | None = None,
    ):
        self.logger.info(
            f"{interaction.user}[ID: {interaction.user.id}] used send-message command"
        )

        # get text
        ctx = await commands.Context.from_interaction(interaction)
        tracker = TextInputTracker(ctx)
        value = await tracker.track_modal(
            title="メッセージの内容を入力してください。",
            custom_id="exts.core.message.send_message_track_modal",
            min_length=1,
            max_length=2000,
            ephemeral=False,
        )
        if not value:
            await ctx.send(content="正しく入力されませんでした。")
            return

        # prepare for do confirm
        checker = Checker(self.bot)
        header = (
            f"{channel.mention}へ次のメッセージを送信します。"
            if not attachment
            else f"{channel.mention}へ次のメッセージを送信します。\n添付ファイルの数は1件です。"
        )

        # do confirm
        res = await checker.check_role(
            ctx=ctx,
            id=int(os.environ["ADMIN"]),
            header=header,
            text=value,
            run_num=1,
            stop_num=1,
        )

        if not res:
            await ctx.send(content="承認されませんでした。\n実行をキャンセルします。")
            return

        # send text (approved)
        messenger = Messenger(ctx, channel)
        await messenger.send_message(content=value, attachment=attachment)
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(MessageSys(bot))
