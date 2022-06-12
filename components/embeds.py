import discord

from model.color import Color


class EmbedBuilder:
    def __init__(self) -> None:
        pass

    @staticmethod
    def inquiry_view_embed(
        *, value: str, target: discord.User | discord.Member
    ) -> discord.Embed:
        from tools.dt import dt_to_str

        embed = discord.Embed(
            colour=Color.default.value,
            title="お問い合わせ",
            description=value,
        )
        embed.add_field(
            name="user",
            value=target.mention,
        )
        embed.add_field(
            name="user_id",
            value=str(target.id),
        )
        embed.set_footer(text=dt_to_str())
        return embed
