from config import settings

from handlers import common, customers, feedback_requests
from handlers.forms import add_customer_form, add_feedback_request_form

from aiogram import Bot, Dispatcher

import asyncio


async def main() -> None:
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    # Handlers routers
    dp.include_router(common.router)
    dp.include_router(customers.router)
    dp.include_router(feedback_requests.router)

    # Forms routers
    dp.include_router(add_customer_form.router)
    dp.include_router(add_feedback_request_form.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, RuntimeError):
        print("Bot has been stopped.")
