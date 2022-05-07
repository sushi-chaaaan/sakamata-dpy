import asyncio
import os

import discord
from components.escape import EscapeWithCodeBlock
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from model.color import Color
from tools.dt import dt_to_str
from tools.logger import getMyLogger

logger = getMyLogger(__name__)


class ThreadSys(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()

    @commands.Cog.listener(name="on_thread_create")
    async def thread_create(self, thread: discord.Thread):
        embed = discord.Embed(
            title="New Thread Created",
            colour=Color.basic.value,
        )
        embed.set_footer(text=f"{dt_to_str()}")
        if not thread.owner:
            logger.exception(f"{thread.id} has no owner")
            return
        embed.set_author(
            name=thread.owner.display_name,
            icon_url=thread.owner.display_avatar.url,
        )
        if thread.parent:
            embed.add_field(name="Parent channel", value=f"{thread.parent.mention}")
        embed.add_field(name="Thread link", value=f"{thread.mention}")
        embed.add_field(name="Author", value=f"{thread.owner.mention}")
        visibility = "public" if not thread.is_private() else "private"
        embed.add_field(name="Visibility", value=visibility)
        if thread.created_at:
            embed.add_field(name="Created at", value=f"{dt_to_str(thread.created_at)}")
        embed.add_field(
            name="archive duration",
            value=f"{str(thread.auto_archive_duration)} minutes",
        )

    @commands.Cog.listener(name="on_thread_update")
    async def thread_update(self, before: discord.Thread, after: discord.Thread):
        if after.locked and not before.locked:
            return
        elif after.archived and not before.archived:
            await after.edit(archived=False)
            return
        else:
            return

    @app_commands.command(name="add-role-to-thread")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(thread_id="Input thread_id to add role's members")
    @app_commands.describe(role="Choose role to add to thread")
    async def add_member_to_thread(
        self,
        interaction: discord.Interaction,
        thread_id: str,
        role: discord.Role,
    ):
        logger.info(
            f"{interaction.user}[ID: {interaction.user.id}] used add-role-to-thread command"
        )

        await interaction.response.defer(thinking=True)

        # get thread
        thread = interaction.guild.get_thread(int(thread_id))  # type: ignore -> checked by Discord server side
        if not thread:
            await interaction.followup.send(content="スレッドが見つかりませんでした。")
            return

        before_count = len(thread.members)

        await interaction.followup.send(content="ロールメンバーの取得を開始します。")

        # get chunked members
        members = role.members
        chunk: list[str] = []
        _chunk: str = ""

        for member in members:

            # メンションを生成
            m = f"<@{member.id}>"

            # 追加後の文字数が2000文字未満なら_chunkに直接追加する
            # そうでなければ現在の_chunkをchunkに追加したあと,あたらしい_chunkをmで初期化
            if len(_chunk) + len(m) < 2000:
                _chunk += m
            else:
                chunk.append(_chunk)
                # mで初期化
                _chunk = m
        # 最後の_chunkをchunkに追加
        chunk.append(_chunk)

        await interaction.followup.send(
            content=f"ロールメンバーの取得を完了しました。\n{str(len(role.members))}人を{str(len(chunk))}回に分けて\n{thread.mention}に追加します。"
        )

        # send message to edit
        try:
            msg = await thread.send(content="test message")
        except Exception as e:
            logger.exception(f"{thread.name} is not accessible", exc_info=e)
            await interaction.followup.send(
                content=f"{thread.mention}にアクセスできません。\n処理を停止します。"
            )
            return

        # add members to thread
        err_count = 0
        for i, text in enumerate(chunk):
            try:
                await msg.edit(content=f"{text}")
            except Exception as e:
                logger.exception(
                    f"failed to edit message: {msg.id},Index:{str(i)}",
                    exc_info=e,
                )
                err_count += 1
            finally:
                await asyncio.sleep(0.50)
        after_count = len(thread.members)
        await interaction.followup.send(
            content=f"処理を完了しました。\n追加したメンバー数:{str(after_count - before_count)}/{len(role.members)}\nエラー回数:{str(err_count)}"
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
        logger.info(
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
                    content="有効なカテゴリを認識できませんでした。", ephemeral=True
                )
                return
            category = _category

        # get threads
        channels = sorted(category.channels, key=lambda channel: channel.position)
        parsed_channels = [
            ch for ch in channels if not isinstance(ch, discord.CategoryChannel)
        ]

        # parse threads
        board_text = "\n\n".join([self.parse_thread(ch) for ch in parsed_channels])

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
            return f"{channel.mention}\n┗{threads[0].mention}"
        return (
            "\n┣".join([f"{channel.mention}"] + [t.mention for t in threads[:-1]])
            + f"\n┗{threads[-1].mention}"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(ThreadSys(bot))
