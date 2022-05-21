from datetime import datetime, timedelta

from discord import Guild, Member, User
from exts.core.system_text import AuditLogText, DealText, ErrorText
from model.response import ExecuteResponse
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

    async def do_kick(self, guild: Guild, target: Member) -> ExecuteResponse:
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
            succeeded = False
            exception = e
        else:
            logger.info(text := DealText.kick.value.format(target=target.mention))
            succeeded = True
            exception = None
        return ExecuteResponse(
            succeeded=succeeded, exception=exception, message=text, value=None
        )

    async def do_ban(
        self,
        guild: Guild,
        target: Member,
        delete_message_days: int,
    ) -> ExecuteResponse:
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
            succeeded = False
            exc = e
        else:
            logger.info(text := DealText.ban.value.format(target=target.mention))
            succeeded = True
            exc = None
        return ExecuteResponse(
            succeeded=succeeded, exception=exc, message=text, value=None
        )

    async def do_timeout(
        self,
        target: Member | User,
        until: datetime | timedelta = timedelta(hours=24.0),
    ) -> ExecuteResponse:

        # type check
        if isinstance(target, User):
            return ExecuteResponse(
                succeeded=False,
                exception=None,
                message=ErrorText.notfound.value,
                value=None,
            )

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
            succeeded = False
            exc = e
        else:
            logger.info(text := DealText.timeout.value.format(target=target.mention))
            succeeded = True
            exc = None
        return ExecuteResponse(
            succeeded=succeeded, exception=exc, message=text, value=None
        )
