import os

import discord
from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands
from dotenv import load_dotenv
from model.color import Color
from tools.confirm import Checker
from tools.dt import dt_to_str
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
        self, interaction: discord.Interaction, user: discord.Member
    ) -> None:
        logger.info(
            f"{interaction.user} [ID: {interaction.user.id}] used contex_user command"
        )
        await interaction.response.defer(ephemeral=True)
        embed = self.user_logic(user)
        await interaction.followup.send(embeds=[embed], ephemeral=True)
        return

    def user_logic(self, target: discord.Member | discord.User) -> discord.Embed:
        avatar_url = (
            target.default_avatar.url
            if target.default_avatar == target.display_avatar
            else target.display_avatar.replace(size=1024, static_format="webp")
        )

        embed = discord.Embed(
            title="ユーザー情報照会結果",
            description=f"対象ユーザー: {target.mention}",
            color=Color.basic.value,
        )
        embed.set_footer(text=f"{dt_to_str()}")
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(
            name="Bot?",
            value=f"{'True' if target.bot else 'False'}",
        )
        embed.add_field(
            name="アカウント作成日時",
            value=f"{dt_to_str(target.created_at)}",
        )
        if isinstance(target, discord.Member):
            joined = dt_to_str(target.joined_at) if target.joined_at else "取得できませんでした"
            embed.add_field(
                name="サーバー参加日時",
                value=f"{joined}",
            )
            roles = sorted(target.roles, key=lambda role: role.position, reverse=True)
            text = "\n".join([role.mention for role in roles])
            embed.add_field(
                name=f"所持ロール({len(roles)})",
                value=text,
                inline=False,
            )
        else:
            embed.description = (
                f"\N{Warning Sign}このサーバーにいないユーザーです。\n対象ユーザー: {target.mention}"
            )
        return embed

    @commands.hybrid_command(name="user")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.describe(target="Choose user to search information")
    async def user(
        self,
        ctx: commands.Context,
        target: discord.Member | discord.User,
    ):
        """ユーザー情報照会用コマンド"""
        logger.info(f"{ctx.author}[ID: {ctx.author.id}] used user command")
        await ctx.defer()
        embed = self.user_logic(target)
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
        logger.info(f"{interaction.user}[ID: {interaction.user.id}] used kick command")
        if not isinstance(target, discord.Member):
            await interaction.response.send_message(content="対象がサーバー内に見つかりませんでした")
            return

        await interaction.response.defer()

        ctx = await commands.Context.from_interaction(interaction)
        if not isinstance(ctx.channel, discord.abc.Messageable):
            return
        role = ctx.guild.get_role(int(os.environ["ADMIN"]))  # type: ignore -> checked by Discord server side
        if not role:
            return

        # do confirm
        checker = Checker(self.bot)
        header = f"{target.mention}をkickしますか？"
        res = await checker.check_role(
            ctx=ctx,
            watch_role=role,
            header=header,
            run_num=1,
            stop_num=1,
        )
        if res:
            df_reason = f"kicked by: {ctx.author.mention}"
            _reason = (
                df_reason if not reason else df_reason + f"\nCustom_Reason: {reason}"
            )
            try:
                await interaction.guild.kick(target, reason=_reason)  # type: ignore -> checked by Discord server side
            except discord.Forbidden as e:
                text = "Failed to kick member: Missing permissions"
                logger.error(text, exc_info=e)
            except Exception as e:
                text = "Failed to kick member: Unknown error"
                logger.error(text, exc_info=e)
            else:
                await ctx.send(content=f"{target.mention}をkickしました")
                return
        else:
            await ctx.send(content="Canceled")
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
        logger.info(f"{interaction.user}[ID: {interaction.user.id}] used ban command")
        if not isinstance(target, discord.Member):
            await interaction.response.send_message(content="対象がサーバー内に見つかりませんでした")
            return

        await interaction.response.defer()

        ctx = await commands.Context.from_interaction(interaction)
        if not isinstance(ctx.channel, discord.abc.Messageable):
            return
        role = ctx.guild.get_role(int(os.environ["ADMIN"]))  # type: ignore -> checked by Discord server side
        if not role:
            return

        # do confirm
        checker = Checker(self.bot)
        header = f"{target.mention}をbanしますか？"
        res = await checker.check_role(
            ctx=ctx,
            watch_role=role,
            header=header,
            run_num=1,
            stop_num=1,
        )
        if res:
            df_reason = f"banned by: {ctx.author.mention}"
            _reason = (
                df_reason if not reason else df_reason + f"\nCustom_Reason: {reason}"
            )
            try:
                await interaction.guild.ban(target, reason=_reason, delete_message_days=delete_message_days)  # type: ignore -> checked by Discord server side
            except discord.Forbidden as e:
                text = "Failed to ban member: Missing permissions"
                logger.error(text, exc_info=e)
            except Exception as e:
                text = "Failed to ban member: Unknown error"
                logger.error(text, exc_info=e)
            else:
                await ctx.send(
                    content=f"{target.mention}をbanしました。\nメッセージ削除期間: {str(delete_message_days)}日間"
                )
                return
        else:
            await ctx.send(content="Canceled")
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
