from dataclasses import dataclass

import discord
from discord import Member, User


@dataclass
class Word:
    content: str
    level: str


@dataclass
class Link:
    content: str
    level: str = "high"


@dataclass
class Detected:
    author: User | Member
    channel: discord.TextChannel | discord.VoiceChannel | discord.Thread
    high: tuple[Word] | None = None
    low: tuple[Word] | None = None
    link: tuple[Link] | None = None
