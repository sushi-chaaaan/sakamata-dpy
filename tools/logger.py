import logging
import logging.handlers
import os

from discord_handler import DiscordHandler
from dotenv import load_dotenv

load_dotenv()


def getMyLogger(name, webhook_url: str | None = None):

    # get logger and handler
    logger = logging.getLogger(name)
    streamHandler = logging.StreamHandler()
    file_handler = logging.handlers.RotatingFileHandler(
        f"./log/{name}.log",
        maxBytes=10**6,
        backupCount=10,
        encoding="utf-8",
        mode="w",
    )
    if not webhook_url:
        webhook_url = os.environ["LOGGER_WEBHOOK_URL"]
    discord_handler = DiscordHandler(
        webhook_url=webhook_url,
        notify_users=[int(os.environ["BOT_OWNER"])],
    )

    # set format
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    streamHandler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    discord_handler.setFormatter(formatter)

    # set level
    logger.setLevel(logging.DEBUG)
    streamHandler.setLevel(logging.DEBUG)
    file_handler.setLevel(logging.DEBUG)
    discord_handler.setLevel(logging.WARNING)

    # add handler
    logger.addHandler(streamHandler)
    logger.addHandler(file_handler)
    logger.addHandler(discord_handler)
    return logger
