import asyncio
import json
from typing import List, Union

import telegram
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from flask import Flask
from hikari import GatewayBot, undefined
from hikari.events.message_events import GuildMessageCreateEvent
from hikari.intents import Intents
from hikari.messages import Mentions

from discord import rest_send_message

# Configuring Flask
app = Flask(__name__)
app.config.from_file("config.json", load=json.load)

async def start_bot():
    members = app.config.get("MEMBERS")

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

    # Set Scheduler
    # scheduler = AsyncIOScheduler()

    # genshin_daily_reminder_members = app.config.get("GENSHIN_DAILY_REMINDER_MEMBERS")
    # genshin_daily_reminder_members_id_list = [members[x]['DISCORD_ID'] for x in genshin_daily_reminder_members]
    
    # TODO CHANGE THE SCHEDULE
    # @scheduler.scheduled_job('interval', seconds=10)
    # async def send_genshin_daily_reminder():
    #     genshin_daily_reminder_message = "Ingat daily Genshin gan!"
    #     await rest_send_message(
    #         discord_bot,
    #         discord_channel_id,
    #         genshin_daily_reminder_message,
    #         genshin_daily_reminder_members_id_list
    #     )
    
    # scheduler.start()

    await discord_bot.start()

loop = asyncio.get_event_loop()
try:
    asyncio.ensure_future(start_bot())
    loop.run_forever()
finally:
    loop.close()
