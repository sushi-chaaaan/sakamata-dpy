import discord
from dotenv import load_dotenv

from model.response import ExecuteResponse
from model.system_text import ErrorText
from tools.logger import getMyLogger


class Finder:
    def __init__(self, bot: discord.Client) -> None:
        load_dotenv()
        self.bot = bot
        self.logger = getMyLogger(__name__)

    async def search_channel(self, channel_id: int) -> ExecuteResponse:
        channel = self.bot.get_channel(channel_id)
        if not channel:
            try:
                channel = await self.bot.fetch_channel(channel_id)
            except Exception as e:
                self.logger.exception(
                    text := ErrorText.notfound.value, exc_info=e)
                return ExecuteResponse(succeeded=False, message=text, exception=e)
        return ExecuteResponse(succeeded=True, message="", value=channel)
