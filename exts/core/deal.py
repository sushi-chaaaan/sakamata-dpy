import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from model.color import Color
from tools.confirm import Confirm
from tools.dt import dt_to_str
from tools.logger import getMyLogger

logger = getMyLogger(__name__)


class Deal(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.confirm = Confirm(bot)
        load_dotenv()

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
        avatar_url = (
            target.default_avatar.url
            if target.default_avatar == target.display_avatar
            else target.display_avatar.replace(size=1024, static_format="webp")
        )
        await ctx.defer()
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
        await ctx.send(embeds=[embed])
        return

    @app_commands.command(name="kick")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(target="Choose user to kick")
    async def kick(
        self, interaction: discord.Interaction, target: discord.Member | discord.User
    ):
        """kick用コマンド"""
        logger.info(f"{interaction.user}[ID: {interaction.user.id}] used kick command")
        await interaction.response.defer()

        # get channel and role
        if not isinstance(target, discord.Member):
            await interaction.followup.send(content="対象が見つかりませんでした")
            return
        ctx = await commands.Context.from_interaction(interaction)
        channel = ctx.channel
        if not isinstance(channel, discord.abc.Messageable):
            return
        role = ctx.guild.get_role(int(os.environ["ADMIN"]))  # type: ignore -> checked by Discord server side
        if not role:
            return

        # do confirm
        header = f"{target.mention}をkickしますか？"
        res = await self.confirm.confirm(
            ctx=ctx,
            watch_role=role,
            header=header,
            run_num=1,
            stop_num=1,
        )
        if res:
            try:
                await interaction.guild.kick(target)  # type: ignore -> checked by Discord server side
            except discord.Forbidden as e:
                text = "Failed to kick member: Missing permissions"
                logger.error(text, exc_info=e)
            except Exception as e:
                text = "Failed to kick member: Unknown error"
                logger.error(text, exc_info=e)
            finally:
                await ctx.send(content=header)
                return
        else:
            await ctx.send(content="Canceled")
            return

    @app_commands.command(name="ban")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(target="Choose user to ban")
    async def ban(
        self, interaction: discord.Interaction, target: discord.Member | discord.User
    ):
        logger.info(f"{interaction.user}[ID: {interaction.user.id}] used ban command")
        pass

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
