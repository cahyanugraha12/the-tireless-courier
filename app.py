import asyncio
import json

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from flask import Flask
from hikari import GatewayBot
from hikari.events.message_events import GuildMessageCreateEvent
from hikari.intents import Intents

from discord import rest_send_message


# Configuring Flask
app = Flask(__name__)
app.config.from_file("config.json", load=json.load)

async def start_bot():
    # Config Discord Bot Setup
    members = app.config.get("MEMBERS")
    discord_bot_token = app.config.get("DISCORD_BOT_TOKEN")
    discord_channel_id = app.config.get("DISCORD_CHANNEL_ID")
        
    # Running Discord Bot
    discord_bot = GatewayBot(
        token=discord_bot_token,
        intents=Intents.GUILD_MESSAGES
    )

    if discord_bot:
        # Set Listener 
        @discord_bot.listen(GuildMessageCreateEvent)
        async def listen_to_message_in_server(event: GuildMessageCreateEvent):
            print(event)

        # Set Scheduler
        scheduler = AsyncIOScheduler()

        genshin_daily_reminder_members = app.config.get("GENSHIN_DAILY_REMINDER_MEMBERS")
        genshin_daily_reminder_members_id_list = [members[x]['DISCORD_ID'] for x in genshin_daily_reminder_members]
        
        # TODO CHANGE THE SCHEDULE
        @scheduler.scheduled_job('interval', seconds=10)
        async def send_genshin_daily_reminder():
            genshin_daily_reminder_message = "Ingat daily Genshin gan!"
            await rest_send_message(
                discord_bot,
                discord_channel_id,
                genshin_daily_reminder_message,
                genshin_daily_reminder_members_id_list
            )
        
        scheduler.start()

        await discord_bot.start()

loop = asyncio.get_event_loop()
try:
    asyncio.ensure_future(start_bot())
    loop.run_forever()
finally:
    loop.close()