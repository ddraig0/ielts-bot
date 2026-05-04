import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import start, reading, listening, writing, speaking, subscription, admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Register routers
    dp.include_router(start.router)
    dp.include_router(subscription.router)
    dp.include_router(reading.router)
    dp.include_router(listening.router)
    dp.include_router(writing.router)
    dp.include_router(speaking.router)
    dp.include_router(admin.router)

    logger.info("IELTS Bot başladı...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
