import asyncio

from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router
from app import database as db

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def on_startup():
    '''
    Функция для создания базы данных в случае ее отсутсвия
    '''
    try:
        await db.db_start()     
    except Exception as e:
        print(f'Ошибка при создании БД: {e}')


async def main():
    dp.include_router(router)
    dp.startup.register(on_startup)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот завершил работу')
    except Exception as e:
        print(f'Ошибка {e}')