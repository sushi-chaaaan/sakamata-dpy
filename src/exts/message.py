import os

import discord
from discord import app_commands
from discord.ext import commands
from dispander import dispand
from dotenv import load_dotenv

from components.embeds import EmbedBuilder as EB
from ext_modal.components.message_input import MessageInputView
from tools.checker import Checker
from tools.log_formatter import command_log
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
    @app_commands.describe(channel="メッセージを送信するチャンネルを選択してください")
    @app_commands.describe(attachment="添付するファイルがあれば添付してください。")
    @app_commands.rename(channel="送信先チャンネル")
    @app_commands.rename(attachment="添付ファイル")
    async def send_message(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel | discord.VoiceChannel | discord.Thread,
        attachment: discord.Attachment | None = None,
    ):
        """メッセージを送信します。"""

        self.logger.info(command_log(
            name="send_message", author=interaction.user))

        ctx = await commands.Context.from_interaction(interaction)

        # get text
        view = MessageInputView(custom_id="src.exts.message.send_message")
        await ctx.send(
            embeds=[
                EB.message_input_preview_embed(
                    author=interaction.user, target=channel, command=True
                )
            ],
            view=view,
        )
        await view.wait()

        if not view.status:
            return

        text = view.content

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
            text=text,
            run_num=1,
            stop_num=1,
        )

        if not res:
            await ctx.send(content="承認されませんでした。\n実行をキャンセルします。")
            return

        # send text (approved)
        messenger = Messenger(ctx, channel)
        await messenger.send_message(content=text, attachment=attachment)
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(MessageSys(bot))
