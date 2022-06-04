import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from cloudflare.client import ImageClient


class Uploader(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()

    @app_commands.command(name="upload")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(image="upload image")
    async def upload(self, interaction: discord.Interaction, image: discord.Attachment):

        if not image.content_type:
            return

        if not image.content_type.startswith("image/"):
            await interaction.response.send_message("upload image plz", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        client = ImageClient()
        res_dict = client.upload_image_from_url(image.url)
        if not res_dict:
            await interaction.followup.send("failed")
            return
        await interaction.followup.send(res_dict["result"]["variants"][0])
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(Uploader(bot))
