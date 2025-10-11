from config import settings

from handlers import common, customers
from handlers.forms import add_customer_form

from aiogram import Bot, Dispatcher

import asyncio


async def main() -> None:
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    # Handlers routers
    dp.include_router(common.router)
    dp.include_router(customers.router)

    # Forms routers
    dp.include_router(add_customer_form.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, RuntimeError):
        print("Bot has been stopped.")
