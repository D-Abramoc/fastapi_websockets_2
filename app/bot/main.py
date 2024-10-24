import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.core.config import bot_settings
from app.bot.handlers import router as start_router

logger = logging.getLogger(__name__)

bot = Bot(token=bot_settings.bot_token.get_secret_value())


async def main(bot):
    '''Start bot.'''
    logging.basicConfig(
        format="[%(asctime)s] [%(name)s] [%(levelname)s] > %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.DEBUG,
    )
    logger.debug("-> Bot online")

    bot: Bot = bot
    dp = Dispatcher()
    dp.include_routers(start_router,)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main(bot))
