import asyncio
import logging

from data import bot
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router


async def main() -> None:
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher.include_router(router=router)

    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dispatcher.start_polling(
            bot,
            allowed_updates=dispatcher.resolve_used_update_types()
        )
    finally:
        dispatcher.shutdown()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
