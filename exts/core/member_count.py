import os

import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from tools.logger import getMyLogger
from tools.search import Finder


class MemberCounter(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()
        self.logger = getMyLogger(__name__)

    def cog_unload(self) -> None:
        self.refresh_count.cancel()

    # set up a task to refresh the member count every 30 minutes
    @tasks.loop(minutes=30.0)
    async def refresh_count(self):
        await self._refresh_count()

    @refresh_count.before_loop
    async def before_refresh_count(self):
        await self.bot.wait_until_ready()

    # refresh member count
    async def _refresh_count(self):

        # get guild
        finder = Finder(self.bot)
        guild_res = await finder.search_guild(int(os.environ["GUILD_ID"]))
        if not guild_res.succeeded:
            return

        if not isinstance((guild := guild_res.value), discord.Guild):
            self.logger.exception(f"{str(guild_res.value)} is not a guild")
            return

        # get channel

        res = await finder.search_channel(int(os.environ["COUNT_VC"]), guild=guild)
        if not res.succeeded:
            return

        # check channel
        if not isinstance((ch := res.value), discord.VoiceChannel):
            self.logger.exception(f"{str(res.value)} is not a VoiceChannel")
            return

        try:
            await ch.edit(
                name="Member Count: {count}".format(
                    count=guild.member_count
                    if guild.member_count
                    else len(guild.members)
                )
            )
        except Exception as e:
            self.logger.exception(f"failed to edit channel: {ch.name}", exc_info=e)
        else:
            self.logger.info(f"updated channel: {ch.name}")
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(MemberCounter(bot))
