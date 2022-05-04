import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv

from tools.logger import getMyLogger

logger = getMyLogger(__name__)

accept_emoji = "\N{Heavy Large Circle}"
reject_emoji = "\N{Cross Mark}"


class Confirm:
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()

    async def confirm(
        self,
        *,
        ctx: commands.Context,
        watch_role: discord.Role | list[discord.Role],
        text: str,
        run_num: int,
        stop_num: int,
    ) -> bool:

        # setup role list
        watch_roles = (
            [watch_role] if isinstance(watch_role, discord.Role) else watch_role
        )
        watch_ids = [r.id for r in watch_roles]
        watch_mentions = "\n".join([f"{role.mention}" for role in watch_roles])

        # send message to watch
        send_text = (
            "【コマンド実行確認】\n------------------------\n"
            + text
            + f"\n------------------------\nコマンド承認:{watch_mentions}\n実行に必要な承認人数: {str(run_num)}\n中止に必要な承認人数: {str(stop_num)}"
        )
        target = await ctx.send(content=send_text)
        await target.add_reaction(accept_emoji)
        await target.add_reaction(reject_emoji)

        # wait for reaction

        def check(payload: discord.RawReactionActionEvent):
            return (
                payload.message_id == target.id
                and payload.emoji.name in [accept_emoji, reject_emoji]
                and payload.member is not None
                and payload.member.id != self.bot.user.id  # type: ignore -> it has no problem if bot is successfully started
                and [r.id for r in payload.member.roles if r.id in watch_ids]
                is not None
            )

        try:
            payload: discord.RawReactionActionEvent = await self.bot.wait_for(
                "raw_reaction_add", check=check, timeout=600.0
            )
        except asyncio.TimeoutError as e:
            await ctx.send(content="タイムアウトしたため処理を停止します。")
            logger.exception("Confirm timeout", exc_info=e)
            result = False
        else:
            if payload.emoji.name == accept_emoji:
                # accept
                result = True
            else:
                # reject
                result = False
        return result
