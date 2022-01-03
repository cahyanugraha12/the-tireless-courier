import asyncio
import importlib
import json
from typing import Any, Dict, List, Union

import telegram
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from flask import Flask
from hikari import GatewayBot, undefined
from hikari.events.message_events import GuildMessageCreateEvent
from hikari.intents import Intents

from discord.interfaces import IDiscordSchedule

# Configuring Flask
app = Flask(__name__)
app.config.from_file("config.json", load=json.load)

async def start_bot():
    members: Dict[str, Any] = app.config.get("MEMBERS")

    # Config Discord Bot Setup
    discord_bot_token = app.config.get("DISCORD_BOT_TOKEN")
    discord_bot_id = app.config.get("DISCORD_BOT_ID")
    discord_channel_id = app.config.get("DISCORD_CHANNEL_ID")
    discord_id_to_members_mapping = app.config.get("DISCORD_ID_TO_MEMBERS_MAPPING")
        
    # Creating Discord Bot
    discord_bot = GatewayBot(
        token=discord_bot_token,
        intents=Intents.GUILD_MESSAGES
    )

    # Config Telegram Bot
    telegram_bot_token = app.config.get("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = app.config.get("TELEGRAM_CHAT_ID")

    # Creating Telegram Bot
    telegram_bot = telegram.Bot(token=telegram_bot_token)

    # Set Listener 
    @discord_bot.listen(GuildMessageCreateEvent)
    async def listen_to_message_in_server(event: GuildMessageCreateEvent):
        if str(event.author_id) != discord_bot_id and str(event.channel_id) == discord_channel_id:
            author = members[discord_id_to_members_mapping[str(event.author_id)]]

            # User Notification on Mention from Discord
            mentioned_user_ids: Union[List[str], undefined.UNDEFINED] = event.message.mentions.user_ids
            if mentioned_user_ids is not undefined.UNDEFINED:
                mentioned_members = [members[discord_id_to_members_mapping[str(user_id)]]
                    if str(user_id) in discord_id_to_members_mapping else None
                    for user_id in mentioned_user_ids
                ]
                for member in mentioned_members:
                    if member and member["SEND_NOTIFICATION_ON_MENTION"]:
                        text = "{}: Hi {}! {} is mentioning you in Discord!".format(
                            member["TELEGRAM_USERNAME"],
                            member["NAME"],
                            author["NAME"]
                        )
                        telegram_bot.send_message(
                            chat_id=telegram_chat_id,
                            text=text,
                            entities=[
                                telegram.MessageEntity(
                                    type="mention",
                                    offset=0,
                                    length=len(member["TELEGRAM_USERNAME"])
                                )
                            ]
                        )

    # Set Scheduler if Enabled
    enable_scheduler = app.config.get("ENABLE_SCHEDULED_MESSAGE")
    if enable_scheduler:
        timezone = app.config.get("TIMEZONE")
        path_to_scheduler_module = app.config.get("DISCORD_SCHEDULE_MODULE_PATH")
        name_of_scheduler_class = app.config.get("DISCORD_SCHEDULE_CLASS_NAME")
        scheduler_module = importlib.import_module(path_to_scheduler_module)

        scheduler = AsyncIOScheduler()

        discord_scheduler: IDiscordSchedule = getattr(scheduler_module, name_of_scheduler_class)

        scheduler = discord_scheduler.add_schedules(scheduler, timezone, discord_bot, discord_channel_id, members)
        
        scheduler.start()

    await discord_bot.start()

loop = asyncio.get_event_loop()
try:
    asyncio.ensure_future(start_bot())
    loop.run_forever()
finally:
    loop.close()
