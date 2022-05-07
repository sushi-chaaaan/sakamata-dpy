import os

import discord
from components.text_input import TextInputTracker
from discord import app_commands
from discord.ext import commands
from dispander import dispand
from dotenv import load_dotenv
from tools.logger import getMyLogger

logger = getMyLogger(__name__)


class MessageSys(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()

    @commands.Cog.listener("on_message")
    async def on_message_dispand(self, message: discord.Message):
        # ignore message not from Guild or Bot
        if (
            not isinstance(message.channel, discord.abc.GuildChannel)
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
        # get text
        ctx = await commands.Context.from_interaction(interaction)
        tracker = TextInputTracker(ctx)
        value = await tracker.track_modal(
            title="メッセージ入力",
            custom_id="exts.core.message.send_message_track_modal",
            min_length=1,
            max_length=2000,
        )
        if not value:
            await interaction.followup.send(content="正しく入力されませんでした。")
            return

        # send text
        try:
            if attachment:
                await channel.send(content=value, file=await attachment.to_file())
            else:
                await channel.send(content=value)
        except Exception as e:
            logger.error(f"failed to send message to {channel.name}", exc_info=e)
            await interaction.followup.send()


async def setup(bot: commands.Bot):
    await bot.add_cog(MessageSys(bot))
