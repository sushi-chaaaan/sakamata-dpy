from enum import Enum

import discord


class Color(Enum):
    default = discord.Colour(0x3498DB)
    notice = discord.Colour(0xFFDD00)
    warning = discord.Colour(0xD0021B)
    admin = discord.Colour(0xF097BD)
