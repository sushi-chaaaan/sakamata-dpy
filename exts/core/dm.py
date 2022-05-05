import os

import discord
from components.text_input import TextInputTracker
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv


class DMSys(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()

    @app_commands.command(name="send-dm")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(target="Choose user to send DM")
    async def send_dm(self, interaction: discord.Interaction, target: discord.Member):
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)
        tracker = TextInputTracker()
        value = await tracker.track_modal(
            ctx=ctx,
            title="DM内容入力",
            custom_id="exts.core.dm.send_dm_track_modal",
            min_length=1,
            max_length=2000,
            timeout=None,
        )
        if not value:
            value = "Canceled"
        await interaction.followup.send(content=value)


async def setup(bot: commands.Bot):
    await bot.add_cog(DMSys(bot))
