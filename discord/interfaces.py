from abc import ABC, abstractstaticmethod
from typing import Any, Dict
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from hikari.impl.bot import GatewayBot


class IDiscordSchedule(ABC):
    @abstractstaticmethod
    def add_schedules(scheduler: AsyncIOScheduler, timezone: str, discord_bot: GatewayBot, discord_channel_id: str, members: Dict[str, Any]) -> AsyncIOScheduler:
        raise NotImplementedError
