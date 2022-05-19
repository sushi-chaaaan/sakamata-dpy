import discord
from components.text_input import TextInputTracker
from discord import ui
from discord.ext import commands
from dotenv import load_dotenv


class Inquiry(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()


class InquiryView(ui.View):
    def __init__(self, *, timeout: float | None = None):
        super().__init__(timeout=timeout)

    @ui.button(
        label="お問い合わせ",
        custom_id="exts.core.inquiry.inquiry_view",
        style=discord.ButtonStyle.blurple,
        emoji="\N{Pencil}",
        row=0,
    )
    async def inquiry_button(
        self, interaction: discord.Interaction, button: ui.Button
    ) -> None:

        # get context
        tracker = TextInputTracker(await commands.Context.from_interaction(interaction))

        # get text input
        value = await tracker.track_modal(
            title="お問い合わせ内容を入力してください。",
            custom_id="exts.core.inquiry.inquiry_button",
            min_length=1,
            max_length=2000,
            direct=True,
        )

        if not value:
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(Inquiry(bot))
