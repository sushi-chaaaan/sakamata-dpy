import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv

from tools.logger import getMyLogger

logger = getMyLogger(__name__)

accept_emoji = "\N{Heavy Large Circle}"
reject_emoji = "\N{Cross Mark}"


class Checker:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()

    async def check_role(
        self,
        *,
        ctx: commands.Context,
        id: int | list[int],
        header: str,
        text: str | None = None,
        run_num: int,
        stop_num: int,
    ) -> bool:

        # setup role list
        if not ctx.guild:
            return False

        if isinstance(id, int):
            watch_ids = [id]
        else:
            watch_ids = id

        watch_roles = [r for i in watch_ids if (r := ctx.guild.get_role(i)) is not None]

        if not watch_roles:
            return False

        watch_mentions = "\n".join([f"<@&{i}>" for i in watch_ids])

        # send message to watch
        suffix = f"\n------------------------\nコマンド承認:{watch_mentions}\n実行に必要な承認人数: {str(run_num)}\n中止に必要な承認人数: {str(stop_num)}"

        if not text:
            send_text = f"【コマンド実行確認】\n{header}" + suffix
        else:
            send_text = (
                f"【コマンド実行確認】\n{header}\n------------------------\n{text}" + suffix
            )
        conf_message = await ctx.send(content=send_text)
        await conf_message.add_reaction(accept_emoji)
        await conf_message.add_reaction(reject_emoji)

        def check(reaction: discord.Reaction, user: discord.User | discord.Member):
            return (
                reaction.message.id == conf_message.id
                and str(reaction.emoji) in [accept_emoji, reject_emoji]
                and isinstance(user, discord.Member)
                and user.id != self.bot.user.id  # type: ignore
                and [i for r in user.roles if (i := r.id) in watch_ids] is not None
                and self._check_counts(reaction.message, run_num, stop_num) is True
            )

        try:
            reaction, user = await self.bot.wait_for(
                "reaction_add", check=check, timeout=600.0
            )
        except asyncio.TimeoutError as e:
            await ctx.send(content="タイムアウトしたため処理を停止します。")
            logger.exception("Confirm timeout", exc_info=e)
            return False
        else:
            if str(reaction.emoji) == accept_emoji:
                # accept
                return True
            else:
                # reject
                return False

    async def check_raw_role(
        self,
        *,
        ctx: commands.Context,
        id: int | list[int],
        header: str,
        text: str | None = None,
        run_num: int,
        stop_num: int,
    ) -> bool:

        # setup role list
        if not ctx.guild:
            return False

        if isinstance(id, int):
            ids = [id]
        else:
            ids = id

        watch_roles = [r for i in ids if (r := ctx.guild.get_role(i)) is not None]

        if not watch_roles:
            return False

        watch_mentions = "\n".join([f"<@&{i}>" for i in ids])

        # send message to watch
        suffix = f"\n------------------------\nコマンド承認:{watch_mentions}\n実行に必要な承認人数: {str(run_num)}\n中止に必要な承認人数: {str(stop_num)}"

        if not text:
            send_text = f"【コマンド実行確認】\n{header}" + suffix
        else:
            send_text = (
                f"【コマンド実行確認】\n{header}\n------------------------\n{text}" + suffix
            )
        conf_message = await ctx.send(content=send_text)
        await conf_message.add_reaction(accept_emoji)
        await conf_message.add_reaction(reject_emoji)

        # wait for reaction

        def check(payload: discord.RawReactionActionEvent):
            return (
                payload.message_id == conf_message.id
                and str(payload.emoji) in [accept_emoji, reject_emoji]
                and (mem := payload.member) is not None
                and mem.id != self.bot.user.id  # type: ignore
                and [i for r in mem.roles if (i := r.id) in ids] is not None
            )

        try:
            payload: discord.RawReactionActionEvent = await self.bot.wait_for(
                "raw_reaction_add", check=check, timeout=600.0
            )
        except asyncio.TimeoutError as e:
            await ctx.send(content="タイムアウトしたため処理を停止します。")
            logger.exception("Confirm timeout", exc_info=e)
            return False
        else:
            if payload.emoji.name == accept_emoji:
                # accept
                return True
            else:
                # reject
                return False

    def _check_counts(
        self,
        message: discord.Message,
        run_num: int,
        stop_num: int,
    ):
        # convert emoji to str

        executable = [
            r.count
            for r in message.reactions
            if str(r.emoji) == accept_emoji and r.count == run_num + 1
        ]
        cancelable = [
            r.count
            for r in message.reactions
            if str(r.emoji) == reject_emoji and r.count == stop_num + 1
        ]
        # print([r.count for r in message.reactions])
        # print(executable, cancelable)
        if executable or cancelable:
            return True
        else:
            return False
