import os

import discord
from components.text_input import TextInputTracker
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv


class Report(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()
        self.ctx_menu_report = app_commands.ContextMenu(
            name="report",
            callback=self.report,
            guild_ids=[int(os.environ["GUILD_ID"])],
        )
        self.bot.tree.add_command(self.ctx_menu_report)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(
            self.ctx_menu_report.name,
            type=self.ctx_menu_report.type,
        )

    @app_commands.guild_only()
    async def report(
        self, interaction: discord.Interaction, user: discord.Member
    ) -> None:
        ctx = await commands.Context.from_interaction(interaction)
        tracker = TextInputTracker(ctx=ctx)

        # get text input
        res = await tracker.track_modal(
            title=f"{user}を管理者に通報しますか？",
            custom_id="exts.core.report.report",
            min_length=1,
            max_length=2000,
            ephemeral=True,
        )
        if not res:
            return

        await ctx.send(f"{user}を管理者に通報しました。", ephemeral=True)
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(Report(bot))
