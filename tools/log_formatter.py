import discord


def command_log(*, name: str, author: discord.Member | discord.User) -> str:
    return "{} [ID: {}] user {} command".format(author, author.id, name)
