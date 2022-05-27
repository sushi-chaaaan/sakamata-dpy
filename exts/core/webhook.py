import aiohttp
from discord import Webhook
from model.response import ExecuteResponse
from tools.logger import getMyLogger


async def post_webhook(webhook_url: str, /, **kwargs) -> ExecuteResponse:
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(webhook_url, session=session)
        logger = getMyLogger(__name__)
        try:
            webhook_message = await webhook.send(wait=True, **kwargs)
        except Exception as e:
            logger.exception(
                text := f"failed to post webhook: {webhook_url}", exc_info=e
            )
            return ExecuteResponse(
                succeeded=False,
                message=text,
                exception=e,
            )
        else:
            logger.info(text := f"succeeded to post webhook: {webhook_url}")
            return ExecuteResponse(
                succeeded=True,
                message=text,
                value=webhook_message,
            )
