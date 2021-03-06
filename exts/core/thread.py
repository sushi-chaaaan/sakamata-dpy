import asyncio
import os

import discord
from components.escape import EscapeWithCodeBlock
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from exts.core.embed_builder import EmbedBuilder
from tools.logger import getMyLogger
from tools.search import Finder


class ThreadSys(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()
        self.logger = getMyLogger(__name__)

    @commands.Cog.listener(name="on_thread_create")
    async def thread_create(self, thread: discord.Thread):
        self.logger.info(f"New Thread created: {thread.name}")
        finder = Finder(self.bot)

        response = await finder.search_channel(int(os.environ["LOG_CHANNEL"]))
        if not response.succeeded:
            return

        if not isinstance(
            response.value, discord.TextChannel | discord.Thread | discord.VoiceChannel
        ):
            self.logger.error(
                f"{str(response.value)} is not TextChannel or Thread or VoiceChannel"
            )
            return

        embed = await EmbedBuilder.on_thread_create_embed(thread)

        await response.value.send(embeds=[embed])
        return

    @commands.Cog.listener(name="on_thread_update")
    async def thread_update(self, before: discord.Thread, after: discord.Thread):
        if after.locked and not before.locked:
            return
        elif after.archived and not before.archived:
            await after.edit(archived=False)
            self.logger.info(f"unarchived {after.name}")
            return
        else:
            return

    @app_commands.command(name="add-role-to-thread")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(thread="Select thread to add role's members")
    @app_commands.describe(role="Choose role to add to thread")
    async def add_member_to_thread(
        self,
        interaction: discord.Interaction,
        thread: discord.Thread,
        role: discord.Role,
    ):
        self.logger.info(
            f"{interaction.user}[ID: {interaction.user.id}] used add-role-to-thread command"
        )

        await interaction.response.defer(thinking=True)

        await interaction.followup.send(content="???????????????????????????????????????????????????")
        before_count = len(thread.members)

        # get chunked members
        members = role.members
        chunk: list[str] = []
        _chunk: str = ""

        for member in members:

            # ????????????????????????
            m = f"<@{member.id}>"

            # ????????????????????????2000??????????????????_chunk?????????????????????
            # ??????????????????????????????_chunk???chunk?????????????????????,???????????????_chunk???m????????????
            if len(_chunk) + len(m) < 2000:
                _chunk += m
            else:
                chunk.append(_chunk)
                # m????????????
                _chunk = m
        # ?????????_chunk???chunk?????????
        chunk.append(_chunk)

        await interaction.followup.send(
            content=f"??????????????????????????????????????????????????????\n{str(len(role.members))}??????{str(len(chunk))}???????????????\n{thread.mention}?????????????????????"
        )

        # send message to edit
        try:
            msg = await thread.send(content="test message")
        except Exception as e:
            self.logger.exception(f"{thread.name} is not accessible", exc_info=e)
            await interaction.followup.send(
                content=f"{thread.mention}?????????????????????????????????\n???????????????????????????"
            )
            return

        # add members to thread
        err_count = 0
        for i, text in enumerate(chunk):
            try:
                await msg.edit(content=f"{text}")
            except Exception as e:
                self.logger.exception(
                    f"failed to edit message: {msg.id},Index:{str(i)}",
                    exc_info=e,
                )
                err_count += 1
            finally:
                await asyncio.sleep(0.50)
        after_count = len(thread.members)
        await interaction.followup.send(
            content=f"??????????????????????????????\n???????????????????????????:{str(after_count - before_count)}/{len(role.members)}\n???????????????:{str(err_count)}"
        )
        await msg.delete(delay=180.0)
        return

    @app_commands.command(name="thread-board")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(
        category="Choose category to make board. defaults to current category"
    )
    async def thread_board(
        self,
        interaction: discord.Interaction,
        category: discord.CategoryChannel | None = None,
    ):
        self.logger.info(
            f"{interaction.user}[ID: {interaction.user.id}] used thread-board command"
        )
        await interaction.response.defer(ephemeral=True)

        # get category
        if not category:
            if (
                not interaction.channel
                or not isinstance(interaction.channel, discord.abc.GuildChannel)
                or not (_category := interaction.channel.category)
            ):
                await interaction.followup.send(
                    content="?????????????????????????????????????????????????????????", ephemeral=True
                )
                return
            category = _category

        # get threads
        channels = sorted(category.channels, key=lambda channel: channel.position)
        filtered_channels = [
            ch for ch in channels if not isinstance(ch, discord.CategoryChannel)
        ]

        # parse threads
        board_text = "\n\n".join([self.parse_thread(ch) for ch in filtered_channels])

        # send board
        view = EscapeWithCodeBlock(text=board_text)
        await interaction.followup.send(content=board_text, view=view, ephemeral=True)
        return

    def parse_thread(
        self,
        channel: discord.TextChannel
        | discord.VoiceChannel
        | discord.StageChannel
        | discord.ForumChannel,
    ) -> str:
        if not isinstance(channel, discord.TextChannel):
            return channel.mention
        if not channel.threads or not (
            escaped_threads := [t for t in channel.threads if not t.is_private()]
        ):
            return channel.mention
        threads = sorted(escaped_threads, key=lambda thread: len(thread.name))
        if len(threads) == 1:
            return f"{channel.mention}\n???{threads[0].mention}"
        return (
            "\n???".join([f"{channel.mention}"] + [t.mention for t in threads[:-1]])
            + f"\n???{threads[-1].mention}"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ThreadSys(bot))
