import json
import re

import discord
from discord.ext import commands
from dotenv import load_dotenv


class WordAlert(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def ng_word(self, message: discord.Message):

        # ignore check
        res = self.ignore_message(message)
        if res:
            return

        finder = Finder(message)
        detected = finder.find_all()

    def ignore_message(self, message: discord.Message) -> bool:

        # ignore message not from Guild
        if not isinstance(
            message.channel, discord.TextChannel | discord.VoiceChannel | discord.Thread
        ):
            return True

        # ignore message from Bot
        if message.author.bot or message.author.id == self.bot.user.id:  # type: ignore
            return True

        # ignore webhook message
        if message.webhook_id:
            return True

        return False


class Finder:
    def __init__(self, message: discord.Message) -> None:
        self.content = message.content
        with open(r"src/word_alert.json", mode="r") as f:
            d: dict[str, str] = json.load(f)
        self.dict = d
        self.server_link = re.compile(r"discord.gg/[\w]*")

    def _detect_high(self) -> tuple[str]:
        return tuple(
            [
                word
                for word in self.dict
                if word in self.content and self.dict[word] == "high"
            ]
        )

    def _detect_low(self) -> tuple[str]:
        return tuple(
            [
                word
                for word in self.dict
                if word in self.content and self.dict[word] == "low"
            ]
        )

    def _detect_server_link(self) -> tuple[str]:
        return tuple([link for link in self.server_link.findall(self.content)])

    def find_all(self) -> dict[str, str]:
        d: dict[str, str] = {}
        for e in self._detect_high():
            d[e] = "high"
        for e in self._detect_low():
            d[e] = "low"
        for e in self._detect_server_link():
            d[e] = "server_link"
        return d


async def setup(bot: commands.Bot):
    await bot.add_cog(WordAlert(bot))
