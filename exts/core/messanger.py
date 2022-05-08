import discord
from discord.ext import commands
from tools.logger import getMyLogger

logger = getMyLogger(__name__)


class Messanger:
    def __init__(self, ctx: commands.Context) -> None:
        self.ctx = ctx
        pass

    async def send_message(
        self,
        *,
        target: discord.TextChannel | discord.VoiceChannel | discord.Thread,
        content: str,
        attachment: discord.Attachment | None = None,
        **kwargs,
    ) -> None:
        try:
            if attachment:
                await target.send(
                    content=content, file=await attachment.to_file(), **kwargs
                )
            else:
                await target.send(content=content, **kwargs)
        except discord.Forbidden as e:
            logger.exception(
                f"failed to send message to {target.mention}\n\nMissing Permission",
                exc_info=e,
            )
            await self.ctx.send(content="メッセージの送信に失敗しました。権限が不足しています。")
            return
        except discord.HTTPException as e:
            match e.code:
                case 50008:
                    logger.exception(
                        f"failed to send message to {target.mention}\n\nText in Voice is not enabled yet in this server: {target.guild.name}(ID: {target.guild.id})",
                        exc_info=e,
                    )
                    await self.ctx.send(
                        content="メッセージの送信に失敗しました。\n送信先にボイスチャンネルを指定していた場合、\nこのサーバーではText in Voiceが有効化されていないことによるエラーです。"
                    )
                    return
                case _:
                    logger.exception(
                        f"failed to send message to {target.mention}\n\nHTTPException(plz check log)",
                        exc_info=e,
                    )
                    await self.ctx.send(
                        content="メッセージの送信に失敗しました。(HTTP Exception)\n詳しくはログを参照してください。"
                    )
                    return
        except Exception as e:
            logger.exception(f"failed to send message to {target.name}", exc_info=e)
            await self.ctx.send(
                content="メッセージの送信に失敗しました。\n権限が不足している可能性があります。\nまた、ボイスチャンネルに送信する場合は、サーバーで\nText in Voiceが有効化されているか予め確認してください。"
            )
            return
        else:
            logger.info(f"message sent to {target.name}")
            await self.ctx.send(content="メッセージ送信に成功しました。")
            return
