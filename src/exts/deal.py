import os

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from dotenv import load_dotenv
from model.response import HammerResponse
from model.system_text import ConfirmText, DealText
from tools.checker import Checker
from tools.dt import JST, str_to_dt
from tools.log_formatter import command_log
from tools.logger import getMyLogger

from .embeds import EmbedBuilder
from .hammer import Hammer


class Deal(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()
        self.logger = getMyLogger(__name__)
        self.ctx_menu_user = app_commands.ContextMenu(
            name="user",
            callback=self.ctx_user,
            guild_ids=[int(os.environ["GUILD_ID"])],
        )
        self.ctx_menu_timeout = app_commands.ContextMenu(
            name="timeout 24h",
            callback=self.ctx_timeout,
            guild_ids=[int(os.environ["GUILD_ID"])],
        )
        self.bot.tree.add_command(self.ctx_menu_user)
        self.bot.tree.add_command(self.ctx_menu_timeout)

    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(
            self.ctx_menu_user.name,
            type=self.ctx_menu_user.type,
        )
        self.bot.tree.remove_command(
            self.ctx_menu_timeout.name,
            type=self.ctx_menu_timeout.type,
        )

    @app_commands.guild_only()
    async def ctx_user(
        self, interaction: discord.Interaction, target: discord.Member
    ) -> None:
        await interaction.response.defer(ephemeral=True)
        self.logger.info(command_log(name="ctx_user", author=interaction.user))

        embed = EmbedBuilder.user_embed(target)
        await interaction.followup.send(embeds=[embed], ephemeral=True)
        return

    @app_commands.guild_only()
    async def ctx_timeout(
        self, interaction: discord.Interaction, target: discord.Member
    ) -> None:
        await interaction.response.defer(ephemeral=True)

        self.logger.info(command_log(name="ctx_timeout", author=interaction.user))

        hammer = Hammer(author=interaction.user)
        response: HammerResponse = await hammer.do_timeout(target=target)
        await interaction.followup.send(response.message, ephemeral=True)
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
        await ctx.defer()
        self.logger.info(command_log(name="user", author=ctx.author))
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

        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        # prepare confirm
        self.logger.info(command_log(name="kick", author=ctx.author))
        if not isinstance(target, discord.Member):
            await interaction.response.send_message(content="対象がサーバー内に見つかりませんでした")
            return

        # do confirm
        checker = Checker(self.bot)
        res = await checker.check_role(
            ctx=ctx,
            id=int(os.environ["ADMIN"]),
            header=ConfirmText.kick.value.format(target=target.mention),
            run_num=2,
            stop_num=1,
        )

        # execute
        if res:
            hammer = Hammer(author=interaction.user, reason=reason)
            response: HammerResponse = await hammer.do_kick(interaction.guild, target)  # type: ignore -> checked by Discord server side
            await ctx.send(response.message)
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

        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        # prepare confirm
        self.logger.info(command_log(name="ban", author=ctx.author))
        if not isinstance(target, discord.Member):
            await interaction.response.send_message(content="対象がサーバー内に見つかりませんでした")
            return

        # do confirm
        checker = Checker(self.bot)
        header = ConfirmText.ban.value.format(target=target.mention)
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
            response: HammerResponse = await hammer.do_ban(
                guild=interaction.guild,  # type: ignore -> checked by Discord server side
                target=target,
                delete_message_days=delete_message_days,
            )
            await ctx.send(response.message)
            return

        # cancel
        else:
            await ctx.send(content=DealText.cancel.value)
            return

    @app_commands.command(name="timeout")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(target="Choose user to timeout")
    @app_commands.describe(
        time="Input date to timeout. 20220510 means 2020/05/10 0:00AM JST."
    )
    async def timeout(
        self,
        interaction: discord.Interaction,
        target: discord.Member,
        time: str,
        reason: str | None = None,
    ):
        await interaction.response.defer()
        ctx = await commands.Context.from_interaction(interaction)

        # prepare confirm
        self.logger.info(command_log(name="timeout", author=ctx.author))
        if not isinstance(target, discord.Member):
            await interaction.response.send_message(content="対象がサーバー内に見つかりませんでした")
            return

        # get dt
        dt = str_to_dt(time, timezone=JST(), format="%Y%m%d")

        # do confirm
        checker = Checker(self.bot)
        header = ConfirmText.timeout.value.format(target=target.mention)
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
            response: HammerResponse = await hammer.do_timeout(target=target, until=dt)
            await ctx.send(response.message)
            return

        # cancel
        else:
            await ctx.send(content=DealText.cancel.value)
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(Deal(bot))
