import json
import os
import re

import discord
from discord.ext import commands
from dotenv import load_dotenv
from model.response import ExecuteResponse
from model.word import Detected, Link, Word

from .embed_builder import EmbedBuilder as EB
from .webhook import post_webhook


class WordAlert(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def ng_word(self, message: discord.Message):

        # ignore check
        if self.ignore_message(message):
            return

        finder = Finder(message)
        detected: Detected | None = finder.find_all()
        if not detected:
            return
        embed = EB.word_alert_embed(detected)
        res: ExecuteResponse = await post_webhook(
            os.environ["NG_WEBHOOK_URL"], embeds=[embed]
        )
        return

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
        self.author = message.author
        self.channel: discord.TextChannel | discord.VoiceChannel | discord.Thread = message.channel  # type: ignore

    def _detect_high(self) -> tuple[Word]:
        return tuple(
            [
                Word(content=word, level="high")
                for word in self.dict
                if word in self.content and self.dict[word] == "high"
            ]
        )

    def _detect_low(self) -> tuple[Word]:
        return tuple(
            [
                Word(content=word, level="low")
                for word in self.dict
                if word in self.content and self.dict[word] == "low"
            ]
        )

    def _detect_server_link(self) -> tuple[Link]:
        return tuple(
            [Link(content=link) for link in self.server_link.findall(self.content)]
        )

    def find_all(self) -> Detected | None:
        high = self._detect_high()
        low = self._detect_low()
        link = self._detect_server_link()
        if not high and not low and not link:
            return None
        return Detected(
            author=self.author,
            channel=self.channel,
            high=high,
            low=low,
            link=link,
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(WordAlert(bot))
