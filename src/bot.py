import os
import platform

import discord
from discord.ext import commands
from dotenv import load_dotenv

from model.color import Color
from tools.dt import dt_to_str
from tools.finder import Finder
from tools.io import read_json
from tools.logger import getMyLogger


class ChloeriumBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        intents.typing = False
        super().__init__(command_prefix="//", intents=intents)

        # setup logger
        self.logger = getMyLogger(__name__)

        # setup vars
        self.failed_extensions = []
        self.failed_views = []
        self.synced_commands = 0

    async def setup_hook(self):
        self.load_config()
        await self.load_exts()
        await self.sync_commands()
        await self.setup_view()

    async def on_ready(self):
        await self.send_boot_message()
        self.logger.info("Bot is ready")

    def load_config(self):
        config = read_json(r"config/config.json")
        self.ext_list = config["ext_list"]

    async def load_exts(self, reload: bool = False):

        if not reload:
            # load extensions
            for ext in self.ext_list:
                try:
                    await self.load_extension(ext)
                except Exception as e:
                    self.logger.error(f"Failed to load extension {ext}", exc_info=e)
                    self.failed_extensions.append(ext)
                else:
                    self.logger.info(f"Loaded extension {ext}")
            if not self.failed_extensions:
                self.failed_extensions = ["None"]

        else:
            # reload extensions
            for ext in self.ext_list:
                try:
                    await self.reload_extension(ext)
                except Exception as e:
                    self.logger.error(f"Failed to reload extension {ext}", exc_info=e)
                else:
                    self.logger.info(f"Reloaded extension {ext}")

    async def sync_commands(self):
        # sync command
        try:
            cmd = await self.tree.sync(
                guild=discord.Object(id=int(os.environ["GUILD_ID"]))
            )
            self.synced_commands = len(cmd)
            self.logger.info(f"{self.synced_commands} commands synced")
        except Exception as e:
            self.logger.error(f"Failed to sync command tree: {e}")

    def load_persistent(self) -> list[discord.ui.View]:
        # import persistent views
        from components.confirm import \
            ConfirmView  # noqa: F401(load_persistent)
        from components.message_input import \
            MessageInputView  # noqa: F401(load_persistent)
        from 

        # load persistent views
        persistent_views: list[discord.ui.View] = []

        d: dict[str, dict[str, str]] = read_json(r"config/persistent_view.json")
        for v in d.values():
            cls = locals()[v["class"]]
            for c_id in v["custom_id"]:
                persistent_views.append(cls(custom_id=c_id))
        return persistent_views

    async def setup_view(self):
        # add persistent_view
        persistent_views = self.load_persistent()
        for v in persistent_views:
            try:
                self.add_view(v)
                self.logger.info(f"Added view {v.__class__.__name__}")
            except Exception as e:
                self.logger.error(
                    f"Failed to add persistent view {(fv := str(v))}",
                    exc_info=e,
                )
                self.failed_views.append(fv)
        if not self.failed_views:
            self.failed_views = ["None"]

    def boot_embed(self) -> discord.Embed:
        embed = discord.Embed(
            title="Booted",
            description=f"Time: {dt_to_str()}",
            color=Color.default.value,
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

    async def send_boot_message(self):
        # send boot log
        embed = self.boot_embed()
        finder = Finder(self)
        channel = await finder.find_channel(int(os.environ["LOG_CHANNEL"]))

        if not isinstance(channel, discord.abc.Messageable):
            self.logger.error(
                f"Failed to get Messageable channel {os.environ['LOG_CHANNEL']}"
            )
        else:
            await channel.send(embeds=[embed])

    def run(self):
        load_dotenv()
        super().run(os.environ["DISCORD_BOT_TOKEN"])
