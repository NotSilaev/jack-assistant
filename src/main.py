from config import settings

from handlers import common, customers, feedback_requests
from handlers.forms import add_customer_form, add_feedback_request_form

from scheduler import runSchedule

from aiogram import Bot, Dispatcher

import asyncio
import threading


async def bot_main() -> None:
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


def runBot():
    asyncio.run(bot_main())


def main():
    scheduler_thread = threading.Thread(target=runSchedule, daemon=True)
    scheduler_thread.start()
    runBot()
    

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, RuntimeError):
        print("Bot has been stopped.")
