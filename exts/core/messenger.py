import discord
from discord.ext import commands

from tools.logger import getMyLogger

logger = getMyLogger(__name__)


class Messenger:
    def __init__(
        self,
        ctx: commands.Context,
        channel: discord.TextChannel | discord.VoiceChannel | discord.Thread,
    ) -> None:
        self.ctx = ctx
        self.channel = channel
        pass

    async def send_message(
        self,
        content: str,
        *,
        attachment: discord.Attachment | None = None,
        **kwargs,
    ) -> None:
        try:
            if attachment:
                await self.channel.send(
                    content=content, file=await attachment.to_file(), **kwargs
                )
            else:
                await self.channel.send(content=content, **kwargs)
        except discord.Forbidden as e:
            logger.exception(
                f"failed to send message to {self.channel.mention}\n\nMissing Permission",
                exc_info=e,
            )
            await self.ctx.send(content="メッセージの送信に失敗しました。権限が不足しています。")
            return
        except discord.HTTPException as e:
            match e.code:
                case 50008:
                    logger.exception(
                        f"failed to send message to {self.channel.mention}\n\nText in Voice is not enabled yet in this server: {self.channel.guild.name}(ID: {self.channel.guild.id})",
                        exc_info=e,
                    )
                    await self.ctx.send(
                        content="メッセージの送信に失敗しました。\n送信先にボイスチャンネルを指定していた場合、\nこのサーバーではText in Voiceが有効化されていないことによるエラーです。"
                    )
                    return
                case _:
                    logger.exception(
                        f"failed to send message to {self.channel.mention}\n\nHTTPException(plz check log)",
                        exc_info=e,
                    )
                    await self.ctx.send(
                        content="メッセージの送信に失敗しました。(HTTP Exception)\n詳しくはログを参照してください。"
                    )
                    return
        except Exception as e:
            logger.exception(
                f"failed to send message to {self.channel.name}", exc_info=e
            )
            await self.ctx.send(
                content="メッセージの送信に失敗しました。\n権限が不足している可能性があります。\nまた、ボイスチャンネルに送信する場合は、サーバーで\nText in Voiceが有効化されているか予め確認してください。"
            )
            return
        else:
            logger.info(f"message sent to {self.channel.name}")
            await self.ctx.send(content="メッセージ送信に成功しました。")
            return
