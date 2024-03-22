import asyncio

from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router
from app import database as db

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def on_startup():
    try:
        await db.db_start()
        print('База данных создана')
    except Exception as e:
        print(f'Ошибка при создании БД: {e}')


async def main():
    dp.include_router(router)
    await dp.start_polling(bot, on_startup=on_startup)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')