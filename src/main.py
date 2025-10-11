from config import settings

from handlers import common

from aiogram import Bot, Dispatcher

import asyncio


async def main() -> None:
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    # Handlers routers
    dp.include_router(common.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, RuntimeError):
        print("Bot has been stopped.")
