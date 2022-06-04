from discord import Embed
from dotenv import load_dotenv
from model.color import Color
from tools.logger import getMyLogger


class EmbedBuilder:
    def __init__(self) -> None:
        load_dotenv()
        self.logger = getMyLogger(__name__)

    @staticmethod
    def member_confirm_embed(image_url: str) -> Embed:
        embed = Embed(
            title="メンバーシップ更新手続き",
            color=Color.default.value,
        )
        embed.set_image(url=image_url)
        return embed
