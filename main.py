import asyncio

from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router
from app import database as db
from datetime import datetime

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def on_startup():
    '''
    Функция для создания базы данных в случае ее отсутствия
    '''
    try:
        await db.db_start()     
    except Exception as e:
        print(f'Ошибка при создании БД: {e}')


async def hourly_task():
    while True:
        data = await db.look_at_dates_of_reminders()
        nearest = min(map(lambda x: (datetime.strptime(x[0], '%Y-%m-%d %H:%M:%S'), x[1], x[2]), data), key=lambda x: x[0])
        print(nearest)

        await asyncio.sleep(10)


async def main():
    dp.include_router(router)
    dp.startup.register(on_startup)

    asyncio.create_task(hourly_task())
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот завершил работу')
    except Exception as e:
        print(f'Ошибка {e}')