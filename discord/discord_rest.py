from typing import List, Optional
from hikari import GatewayBot, undefined

async def rest_send_message(
        bot: GatewayBot,
        channel_id: str,
        message: str,
        attachment_url: Optional[str] = None,
        user_mentions: Optional[List[str]] = None
    ) -> None:
    if user_mentions:
        message += " "
        message += "".join([f"<@{id}>" for id in user_mentions])
    else:
        user_mentions = undefined.UNDEFINED
    
    if attachment_url:
        attachment = attachment_url
    else:
        attachment = undefined.UNDEFINED

    await bot.rest.create_message(
        channel=str(channel_id),
        content=message,
        attachment=attachment,
        user_mentions=user_mentions
    )