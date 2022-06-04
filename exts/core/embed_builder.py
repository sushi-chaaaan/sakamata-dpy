import discord

from model.color import Color
from tools.dt import dt_to_str


class EmbedBuilder:
    @staticmethod
    def user_embed(target: discord.Member | discord.User) -> discord.Embed:
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
            value=target.bot,
        )
        embed.add_field(
            name="アカウント作成日時",
            value=f"{dt_to_str(target.created_at)}",
        )
        if isinstance(target, discord.Member):
            joined = dt_to_str(
                target.joined_at) if target.joined_at else "取得できませんでした"
            embed.add_field(
                name="サーバー参加日時",
                value=f"{joined}",
            )
            roles = sorted(
                target.roles, key=lambda role: role.position, reverse=True)
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

    @staticmethod
    async def on_thread_create_embed(thread: discord.Thread) -> discord.Embed:
        embed = discord.Embed(
            title="New Thread Created",
            colour=Color.basic.value,
        )
        embed.set_footer(text=dt_to_str())
        embed.set_author(
            name=thread.owner.display_name if thread.owner else "Unknown",
            icon_url=thread.owner.display_avatar.url if thread.owner else None,
        )
        if thread.parent:
            embed.add_field(name="Parent channel", value=thread.parent.mention)
        embed.add_field(name="Thread link", value=thread.mention)
        embed.add_field(
            name="Owner", value=thread.owner.mention if thread.owner else "Unknown"
        )
        visibility = "public" if not thread.is_private() else "private"
        embed.add_field(name="Visibility", value=visibility)
        if thread.created_at:
            embed.add_field(name="Created at",
                            value=dt_to_str(thread.created_at))
        embed.add_field(
            name="archive duration",
            value=f"{str(thread.auto_archive_duration)} minutes",
        )
        return embed
