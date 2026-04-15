import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ErrorEvent
from aiogram.exceptions import TelegramBadRequest

from registration import router as registration_router
from holidays import holiday_checker
from profile import router as profile_router
from admin_panel import router as admin_router
from rate import router as rate_router
from faq import router as faq_router
from mini_test import router as test_router
from onboarding import router as onboarding_router, onboarding_scheduler
from meeting import router as meeting_router
from meeting_reminders import meeting_reminder_scheduler

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logging.getLogger("aiogram.event").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TG_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


async def _run_forever(coro_fn, *args, name: str):
    while True:
        try:
            await coro_fn(*args)
        except Exception as e:
            logger.error("[%s] упала: %s — перезапуск через 10с", name, e, exc_info=True)
            await asyncio.sleep(10)

async def main():
    dp.include_router(admin_router)
    dp.include_router(onboarding_router)
    dp.include_router(meeting_router)
    dp.include_router(profile_router)
    dp.include_router(rate_router)
    dp.include_router(faq_router)
    dp.include_router(test_router)
    dp.include_router(registration_router)

    @dp.error()
    async def error_handler(event: ErrorEvent):
        if isinstance(event.exception, TelegramBadRequest) and "message is not modified" in str(event.exception):
            return
        logger.error("Необработанная ошибка: %s", event.exception, exc_info=event.exception)

    asyncio.create_task(_run_forever(holiday_checker, bot, name="holiday_checker"))
    asyncio.create_task(_run_forever(onboarding_scheduler, bot, dp, name="onboarding_scheduler"))
    asyncio.create_task(_run_forever(meeting_reminder_scheduler, bot, name="meeting_reminder_scheduler"))

    logger.info("Bot started")

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    asyncio.run(main())
