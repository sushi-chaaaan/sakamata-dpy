from datetime import datetime, timedelta

from discord import Guild, Member, User
from exts.core.system_text import AuditLogText, DealText
from tools.logger import getMyLogger

logger = getMyLogger(__name__)


class Hammer:
    def __init__(
        self,
        *,
        author: User | Member,
        reason: str | None = None,
    ) -> None:
        self.author = author.mention
        self.reason = reason

    async def do_kick(self, guild: Guild, target: Member) -> str:
        try:
            await guild.kick(target, reason=self.reason)
        except Exception as e:
            logger.exception(
                text := DealText.exception.value.format(
                    deal="kick",
                    target=target.mention,
                    exception=e.__class__.__name__,
                ),
                exc_info=e,
            )
            return text
        else:
            logger.info(text := DealText.kick.value.format(target=target.mention))
            return text

    async def do_ban(
        self,
        guild: Guild,
        target: Member,
        delete_message_days: int,
    ) -> str:
        try:
            await guild.ban(
                target,
                reason=AuditLogText.ban.value.format(
                    author=self.author,
                    reason=self.reason,
                ),
                delete_message_days=delete_message_days,
            )
        except Exception as e:
            logger.exception(
                text := DealText.exception.value.format(
                    deal="ban",
                    target=target.mention,
                    exception=e.__class__.__name__,
                ),
                exc_info=e,
            )
            return text
        else:
            logger.info(text := DealText.ban.value.format(target=target.mention))
            return text

    async def do_timeout(
        self,
        target: Member | User,
        until: datetime | timedelta = timedelta(hours=24.0),
    ) -> str:

        # type check
        if isinstance(target, User):
            return "対象がサーバー内に見つかりませんでした"

        try:
            await target.timeout(
                until,
                reason=AuditLogText.timeout.value.format(
                    author=self.author, reason=self.reason
                ),
            )
        except Exception as e:
            logger.exception(
                text := DealText.exception.value.format(
                    deal="timeout",
                    target=target.mention,
                    exception=e.__class__.__name__,
                ),
                exc_info=e,
            )
            return text
        else:
            logger.info(text := DealText.timeout.value.format(target=target.mention))
            return text
