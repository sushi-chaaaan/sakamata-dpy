import os

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from dotenv import load_dotenv
from exts.core.embed_builder import EmbedBuilder
from exts.core.hammer import Hammer
from exts.core.system_text import ConfirmText, DealText
from tools.checker import Checker
from tools.logger import getMyLogger

logger = getMyLogger(__name__)


class Deal(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()
        self.ctx_menu_user = app_commands.ContextMenu(
            name="user",
            callback=self.ctx_user,
            guild_ids=[int(os.environ["GUILD_ID"])],
        )
        self.bot.tree.add_command(self.ctx_menu_user)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(
            self.ctx_menu_user.name,
            type=self.ctx_menu_user.type,
        )

    @app_commands.guild_only()
    async def ctx_user(
        self, interaction: discord.Interaction, target: discord.Member
    ) -> None:
        logger.info(
            "{} [ID: {}] used user ctx_menu command".format(u := interaction.user, u.id)
        )
        await interaction.response.defer(ephemeral=True)
        embed = EmbedBuilder.user_embed(target)
        await interaction.followup.send(embeds=[embed], ephemeral=True)
        return

    @commands.hybrid_command(name="user")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.describe(target="Choose user to search information")
    async def user(
        self,
        ctx: commands.Context,
        target: discord.Member | discord.User,
    ):
        """ユーザー情報照会用コマンド"""
        logger.info("{} [ID: {}] used user command".format(u := ctx.author, u.id))
        await ctx.defer()
        embed = EmbedBuilder.user_embed(target)
        await ctx.send(embeds=[embed])
        return

    @app_commands.command(name="kick")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(target="Choose user to kick")
    async def kick(
        self,
        interaction: discord.Interaction,
        target: discord.Member | discord.User,
        reason: str | None = None,
    ):
        """kick用コマンド"""

        # prepare confirm
        logger.info(f"{interaction.user}[ID: {interaction.user.id}] used kick command")
        if not isinstance(target, discord.Member):
            await interaction.response.send_message(content="対象がサーバー内に見つかりませんでした")
            return

        await interaction.response.defer()

        ctx = await commands.Context.from_interaction(interaction)

        # do confirm
        checker = Checker(self.bot)
        res = await checker.check_role(
            ctx=ctx,
            id=int(os.environ["ADMIN"]),
            header=ConfirmText.kick.value.format(target=target.mention),
            run_num=1,
            stop_num=1,
        )

        # execute
        if res:
            hammer = Hammer(author=interaction.user, reason=reason)
            text = await hammer.do_kick(interaction.guild, target)  # type: ignore -> checked by Discord server side
            await ctx.send(text)
            return

        # cancel
        else:
            await ctx.send(DealText.cancel.value)
            return

    @app_commands.command(name="ban")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(target="Choose user to ban")
    @app_commands.choices(
        delete_message_days=[
            Choice(name="Don't delete any", value=0),
            Choice(name="1 day", value=1),
            Choice(name="2 days", value=2),
            Choice(name="3 days", value=3),
            Choice(name="7 days", value=7),
        ]
    )
    async def ban(
        self,
        interaction: discord.Interaction,
        target: discord.Member | discord.User,
        delete_message_days: int = 3,
        reason: str | None = None,
    ):

        # prepare confirm
        logger.info(f"{interaction.user}[ID: {interaction.user.id}] used ban command")
        if not isinstance(target, discord.Member):
            await interaction.response.send_message(content="対象がサーバー内に見つかりませんでした")
            return

        await interaction.response.defer()

        ctx = await commands.Context.from_interaction(interaction)

        # do confirm
        checker = Checker(self.bot)
        header = f"{target.mention}をbanしますか？"
        res = await checker.check_role(
            ctx=ctx,
            id=int(os.environ["ADMIN"]),
            header=header,
            run_num=1,
            stop_num=1,
        )

        # execute
        if res:
            hammer = Hammer(author=interaction.user, reason=reason)
            text = await hammer.do_ban(
                guild=interaction.guild,  # type: ignore -> checked by Discord server side
                target=target,
                delete_message_days=delete_message_days,
            )
            await ctx.send(text)
            return

        # cancel
        else:
            await ctx.send(content=DealText.cancel.value)
            return

    @app_commands.command(name="timeout")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(target="Choose user to timeout")
    @app_commands.describe(time="Choose time to timeout")
    async def timeout(
        self, interaction: discord.Interaction, target: discord.Member, time: int
    ):
        logger.info(
            f"{interaction.user}[ID: {interaction.user.id}] used timeout command"
        )
        pass


async def setup(bot: commands.Bot):
    await bot.add_cog(Deal(bot))
