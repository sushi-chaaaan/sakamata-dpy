from datetime import datetime, timedelta

from discord import Guild, Member, User
from model.response import HammerResponse
from model.system_text import AuditLogText, DealText
from tools.logger import getMyLogger


class Hammer:
    def __init__(
        self,
        *,
        author: User | Member,
        reason: str | None = None,
    ) -> None:
        self.logger = getMyLogger(__name__)
        self.author = author.mention
        self.reason = reason

    async def do_kick(self, guild: Guild, target: Member) -> HammerResponse:
        try:
            await guild.kick(target, reason=self.reason)
        except Exception as e:
            self.logger.exception(
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
            self.logger.info(text := DealText.kick.value.format(target=target.mention))
            succeeded = True
            exception = None
        return HammerResponse(succeeded=succeeded, message=text, exception=exception)

    async def do_ban(
        self,
        guild: Guild,
        target: Member,
        delete_message_days: int,
    ) -> HammerResponse:
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
            self.logger.exception(
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
            self.logger.info(text := DealText.ban.value.format(target=target.mention))
            succeeded = True
            exc = None
        return HammerResponse(succeeded=succeeded, message=text, exception=exc)

    async def do_timeout(
        self,
        target: Member | User,
        until: datetime | timedelta = timedelta(hours=24.0),
    ) -> HammerResponse:

        # type check
        if isinstance(target, User):
            return HammerResponse(
                succeeded=False,
                exception=None,
                message="Cannot timeout discord.User.",
            )

        try:
            await target.timeout(
                until,
                reason=AuditLogText.timeout.value.format(
                    author=self.author, reason=self.reason
                ),
            )
        except Exception as e:
            self.logger.exception(
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
            self.logger.info(
                text := DealText.timeout.value.format(target=target.mention)
            )
            succeeded = True
            exc = None
        return HammerResponse(succeeded=succeeded, message=text, exception=exc)
