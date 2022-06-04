import discord
from discord.ext import commands
from tools.io import read_json
from tools.logger import getMyLogger
from tools.finder import Finder
from tools.webhook import transfer_message


class Listener(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = getMyLogger(__name__)

    @commands.Cog.listener("on_message")
    async def listen_message(self, message: discord.Message):
        # check author
        if message.author.id == self.bot.user.id:  # type: ignore
            return

        # check webhook
        if message.webhook_id:
            return

        # check channel
        if not isinstance(message.channel, discord.abc.GuildChannel):
            return

        await transfer_message(
            "https://discord.com/api/webhooks/980935337033474099/bBQzrScRA7lWJHK8nsBjjQP8mb6XEtsk-G43iQwF9pXxHEeVIqMXrvnjpHEflx1yC5Cn",
            message=message,
        )
        return

        # init
        finder = Finder(self.bot)

        # check category
        if message.channel.category:
            return

        # search target


async def setup(bot: commands.Bot):
    await bot.add_cog(Listener(bot))
