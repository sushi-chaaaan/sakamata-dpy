import json
import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from model.color import Color


class Poll(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()

    @commands.command(name="poll")
    @commands.guild_only()
    # @commands.has_role?
    async def poll(self, ctx: commands.Context, title: str, *select: str):
        if (options := len(select)) > 20:
            await ctx.reply("選択肢は最大20個までです。")
            return

        # load emoji
        with open(r"src/poll_emoji.json", "r") as f:
            emoji_dict = json.load(f)

        # generate options
        if not select:
            # yes or no
            option = [
                {"name": emoji_dict["0"], "value": "はい"},
                {"name": emoji_dict["1"], "value": "いいえ"},
            ]
        else:
            # many options
            option = [
                {"name": emoji_dict[str(i)], "value": select[i]} for i in range(options)
            ]

        # generate embed
        embed = discord.Embed(
            color=Color.default.value,
            title=title,
        )
        embed.set_author(name="投票")
        for opt in option:
            embed.add_field(**opt)

        # send embed and add reactions
        msg = await ctx.send(embeds=[embed])
        for e in [d["name"] for d in option]:
            await msg.add_reaction(e)
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(Poll(bot))
