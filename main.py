import os
import platform

import discord
from discord.ext import commands
from dotenv import load_dotenv

from model.color import Color
from tools.dt import dt_to_str
from tools.logger import getMyLogger

logger = getMyLogger(__name__)


EXT_LIST = [
    "exts.core.entrance",
    "exts.core.deal",
    "exts.core.dm",
    "exts.core.error",
    "exts.core.message",
    "exts.core.report",
    "exts.core.thread",
    "exts.core.word_alert",
    "exts.utils",
    # "Presentation.image",
]

intents = discord.Intents.all()
intents.typing = False


class MyBot(commands.Bot):
    def __init__(self, intents: discord.Intents, **kwargs):
        super().__init__(
            command_prefix="//",
            intents=intents,
            **kwargs,
        )
        self.persistent_views_added = False
        self.failed_extensions = []
        self.failed_views = []
        self.synced_commands = 0

    async def setup_hook(self):

        # load extensions
        for ext in EXT_LIST:
            try:
                await self.load_extension(ext)
            except Exception as e:
                logger.error(f"Failed to load extension {ext}", exc_info=e)
                self.failed_extensions.append(ext)
            else:
                logger.info(f"Loaded extension {ext}")
        if not self.failed_extensions:
            self.failed_extensions = ["None"]

        # sync command
        try:
            cmd = await self.tree.sync(
                guild=discord.Object(id=int(os.environ["GUILD_ID"]))
            )
            self.synced_commands = len(cmd)
            logger.info(f"{self.synced_commands} commands synced")
        except Exception as e:
            logger.error(f"Failed to sync command tree: {e}")

        # add persistent_view
        VIEWS: list[discord.ui.View] = []
        if not self.persistent_views_added:
            for v in VIEWS:
                try:
                    self.add_view(v)
                except TypeError as e:
                    logger.error(
                        f"[TypeError]\nFailed to add persistent view {v}", exc_info=e
                    )
                    self.failed_views.append(v.__str__())
                except ValueError as e:
                    logger.error(
                        f"[ValueError]\nFailed to add persistent view {v}", exc_info=e
                    )
                    self.failed_views.append(v.__str__())
                except Exception as e:
                    logger.error(
                        f"[Unknown Exception]\nFailed to add persistent view {v}",
                        exc_info=e,
                    )
                    self.failed_views.append(v.__str__())
        if not self.failed_views:
            self.failed_views = ["None"]
        self.persistent_views_added = True

    async def on_ready(self):
        # send boot log
        embed = self._get_embed()
        channel = self.get_channel(int(os.environ["LOG_CHANNEL"]))
        if not channel:
            channel = await self.fetch_channel(int(os.environ["LOG_CHANNEL"]))
        if not isinstance(channel, discord.abc.Messageable):
            logger.error(
                f"Failed to get Messageable channel {os.environ['LOG_CHANNEL']}"
            )
        else:
            await channel.send(embeds=[embed])
        logger.info("Bot is ready")

    def _get_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="Booted",
            description=f"Time: {dt_to_str()}",
            color=Color.basic.value,
        )
        embed.add_field(
            name="Extensions failed to load",
            value="\n".join(self.failed_extensions),
            inline=False,
        )
        embed.add_field(
            name="Views failed to add",
            value="\n".join(self.failed_views),
            inline=False,
        )
        embed.add_field(
            name="loaded app_commands",
            value=self.synced_commands,
            inline=False,
        )
        embed.add_field(
            name="Latency",
            value=f"{self.latency * 1000:.2f}ms",
        )
        embed.add_field(
            name="Python",
            value=f"{platform.python_implementation()} {platform.python_version()}",
        )
        embed.add_field(
            name="discord.py",
            value=f"{discord.__version__}",
        )
        return embed


if __name__ == "__main__":
    load_dotenv()
    bot = MyBot(intents=intents, application_id=int(os.environ["APP_ID"]))
    token = os.environ["DISCORD_BOT_TOKEN"]
    try:
        bot.run(token)
    except Exception as e:
        logger.exception("Failed to run bot", exc_info=e)
