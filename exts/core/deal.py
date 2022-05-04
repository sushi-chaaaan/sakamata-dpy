import os

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from model.color import Color
from tools.dt import dt_to_str
from tools.logger import getMyLogger

logger = getMyLogger(__name__)


class Deal(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv()

    @commands.hybrid_command(name="user")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.describe(target="Choose user to search information")
    async def user(
        self,
        ctx: commands.Context,
        target: discord.Member,
    ):
        joined = dt_to_str(target.joined_at) if target.joined_at else "取得できませんでした"
        avatar_url = (
            target.default_avatar.url
            if target.default_avatar == target.display_avatar
            else target.display_avatar.replace(size=1024, static_format="webp")
        )
        await ctx.defer(ephemeral=True)
        embed = discord.Embed(
            title="ユーザー情報照会結果",
            description=f"対象ユーザー: {target.mention}",
            color=Color.basic.value,
        )
        embed.set_footer(text=f"{dt_to_str()}")
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(
            name="アカウント作成日時",
            value=f"{dt_to_str(target.created_at)}",
        )
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
        await ctx.send(embeds=[embed])
        return

    @app_commands.command(name="kick")
    @app_commands.guilds(discord.Object(id=int(os.environ["GUILD_ID"])))
    @app_commands.guild_only()
    @app_commands.describe(target="Choose user to kick")
    async def kick(self, interaction: discord.Interaction, target: discord.Member):
        await interaction.response.defer(ephemeral=True)
        if not isinstance(target, discord.Member):
            await interaction.followup.send(
                content="target is not discord.Member", ephemeral=True
            )
            return
        text = f"{target.mention} was kicked"
        context = await commands.Context.from_interaction(interaction)
        try:
            await interaction.guild.kick(target)  # type: ignore -> checked by Discord server side
        except discord.Forbidden as e:
            text = "Failed to kick member: Missing permissions"
            logger.error(text, exc_info=e)
        except Exception as e:
            text = "Failed to kick member: Unknown error"
            logger.error(text, exc_info=e)
        finally:
            await interaction.followup.send(content=text)
            return


async def setup(bot: commands.Bot):
    await bot.add_cog(Deal(bot))
