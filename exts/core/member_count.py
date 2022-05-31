import os

import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
from tools.dt import dt_to_str
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
        self.logger.info(
            "next refresh is scheduled at {}".format(
                dt_to_str(self.refresh_count.next_iteration)
                if self.refresh_count.next_iteration
                else "cannot get next iteration"
            )
        )
        res = await self._refresh_count()
        if not res:
            self.logger.error("failed to refresh member count")
        else:
            self.logger.info("refreshed member count")

    @refresh_count.before_loop
    async def before_refresh_count(self):
        await self.bot.wait_until_ready()

    @app_commands.command(name="refresh-member-count")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    async def refresh_count_command(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        res = await self._refresh_count()
        text = "更新しました" if res else "更新に失敗しました"
        await interaction.followup.send(text, ephemeral=True)
        return

    # refresh member count
    async def _refresh_count(self) -> bool:

        # get guild
        finder = Finder(self.bot)
        guild_res = await finder.search_guild(int(os.environ["GUILD_ID"]))
        if not guild_res.succeeded:
            return False

        if not isinstance((guild := guild_res.value), discord.Guild):
            self.logger.exception(f"{str(guild_res.value)} is not a guild")
            return False

        # get channel

        res = await finder.search_channel(int(os.environ["COUNT_VC"]), guild=guild)
        if not res.succeeded:
            return False

        # check channel
        if not isinstance((ch := res.value), discord.VoiceChannel):
            self.logger.exception(f"{str(res.value)} is not a VoiceChannel")
            return False

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
            return False
        else:
            self.logger.info(f"updated channel: {ch.name}")
            return True


async def setup(bot: commands.Bot):
    await bot.add_cog(MemberCounter(bot))
