from typing import List
from hikari import GatewayBot
from hikari.api.rest import RESTClient

async def rest_send_message(bot: GatewayBot, channel_id: str, message: str, user_mentions: List[str]):
    if user_mentions:
        message += " ".join([f"<@{id}>" for id in user_mentions])

    await bot.rest.create_message(
        channel=str(channel_id),
        content=message,
        user_mentions=user_mentions
    )