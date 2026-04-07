import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from registration import router as registration_router
from holidays import holiday_checker
from profile import router as profile_router
from adminpanel import router as admin_router
from rate import router as rate_router
from faq import router as faq_router
load_dotenv()
TOKEN = os.getenv("TG_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def main():

    dp.include_router(admin_router)
    dp.include_router(profile_router)
    dp.include_router(rate_router)
    dp.include_router(faq_router)
    dp.include_router(registration_router)

    asyncio.create_task(holiday_checker(bot))

    print("Bot started")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())