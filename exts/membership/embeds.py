from discord import Embed
from dotenv import load_dotenv
from model.color import Color
from tools.logger import getMyLogger


class EmbedBuilder:
    def __init__(self) -> None:
        load_dotenv()
        self.logger = getMyLogger(__name__)
