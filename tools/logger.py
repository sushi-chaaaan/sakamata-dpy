import logging
import logging.handlers
import os

from discord_handler import DiscordHandler
from dotenv import load_dotenv

load_dotenv()


def getMyLogger(name):

    # get logger and handler
    logger = logging.getLogger(name)
    logger.handlers.clear()
    streamHandler = logging.StreamHandler()
    file_handler = logging.handlers.RotatingFileHandler(
        f"./log/{name}.log", maxBytes=10**6, backupCount=10
    )
    discord_handler = DiscordHandler(
        webhook_url=os.environ["DISCORD_WEBHOOK_URL"],
        notify_users=[450942501889507328],
    )

    # set format
    formatter = logging.Formatter(
        "%(levelname)-9s  %(asctime)s  [%(name)s] %(message)s"
    )
    streamHandler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    discord_handler.setFormatter(formatter)

    # set level
    logger.setLevel(logging.DEBUG)
    streamHandler.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)
    discord_handler.setLevel(logging.WARNING)

    # add handler
    logger.addHandler(streamHandler)
    logger.addHandler(file_handler)
    logger.addHandler(discord_handler)
    return logger
