import discord
from discord.ext import commands
from dotenv import load_dotenv
from model.color import Color
from tools.dt import dt_to_str
from tools.logger import getMyLogger

logger = getMyLogger(__name__)


class ThreadSys(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()

    @commands.Cog.listener(name="on_thread_create")
    async def thread_create(self, thread: discord.Thread):
        embed = discord.Embed(
            title="スレッドが作成されました。",
            colour=Color.basic.value,
        )
        embed.set_footer(text=f"{dt_to_str()}")
        if not thread.owner:
            logger.exception(f"{thread.id} has no owner")
            return
        embed.set_author(
            name=thread.owner.display_name,
            icon_url=thread.owner.display_avatar.url,
        )
        if thread.parent:
            embed.add_field(name="Parent channel", value=f"{thread.parent.mention}")
        embed.add_field(name="Thread link", value=f"{thread.mention}")
        embed.add_field(name="Author", value=f"{thread.owner.mention}")
        visibility = "public" if not thread.is_private() else "private"
        embed.add_field(name="Visibility", value=visibility)
        if thread.created_at:
            embed.add_field(name="Created at", value=f"{dt_to_str(thread.created_at)}")
        embed.add_field(
            name="archive duration",
            value=f"{str(thread.auto_archive_duration)} minutes",
        )

    @commands.Cog.listener(name="on_thread_update")
    async def thread_update(self, before: discord.Thread, after: discord.Thread):
        if after.locked and not before.locked:
            return
        elif after.archived and not before.archived:
            await after.edit(archived=False)
            return
        else:
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(ThreadSys(bot))
