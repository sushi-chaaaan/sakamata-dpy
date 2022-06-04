import discord

from model.system_text import ErrorText

from .logger import getMyLogger


class Finder:
    def __init__(self, bot: discord.Client) -> None:
        self.bot = bot
        self.logger = getMyLogger(__name__)
        self.guild: discord.Guild | None = None

    async def search_channel(
        self, channel_id: int, guild: discord.Guild | None = None
    ) -> discord.abc.GuildChannel | discord.abc.PrivateChannel | discord.Thread:
        self.guild = guild
        channel = self.seek.get_channel(channel_id)
        if not channel:
            try:
                channel = await self.seek.fetch_channel(channel_id)
            except Exception as e:
                self.logger.exception(
                    text := ErrorText.notfound.value, exc_info=e)
                raise Exception(text)
        return channel

    @property
    def seek(self):
        if self.guild:
            return self.guild
        return self.bot

    async def search_guild(self, guild_id: int) -> discord.Guild:
        guild = self.bot.get_guild(guild_id)
        if not guild:
            try:
                guild = await self.bot.fetch_guild(guild_id)
            except Exception as e:
                self.logger.exception(
                    text := ErrorText.notfound.value, exc_info=e)
                raise Exception(text)
        return guild
