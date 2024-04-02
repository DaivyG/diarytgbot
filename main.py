import asyncio

from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router
from app import database as db
from datetime import datetime, timedelta

bot = Bot(token=TOKEN)
dp = Dispatcher()

#при нажатии далее если ни один пользователь не выбран бот работает дальше

async def on_startup():
    '''
    Функция для создания базы данных в случае ее отсутствия
    '''
    try:
        await db.db_start()     
    except Exception as e:
        print(f'Ошибка при создании БД: {e}')


async def send_message(chat_ids, heading, period, datetime_of_event:datetime, _id, frequency):
    try:
        for chat_id in chat_ids:
            await bot.send_message(chat_id, [f'До события {heading} осталось {period}', f'Событие {heading} только что наступило'][period == 'Сейчас'])
        
        if period == 'Сейчас':
            if frequency == 'Единично':
                await db.delete_my_event(_id)
            elif frequency == 'Ежедневно':
                await db.change_datetime(datetime_of_event.replace(day=datetime_of_event.day + 1), _id)
            elif frequency == 'Еженедельно':
                await db.change_datetime(datetime_of_event.replace(day=datetime_of_event.day + 7), _id)
            elif frequency == 'Ежемесячно':
                await db.change_datetime(datetime_of_event.replace(day=datetime_of_event.month + 1), _id)
            elif frequency == 'Ежегодно':
                await db.change_datetime(datetime_of_event.replace(day=datetime_of_event.year + 1), _id)

        return True

    except Exception as e:
        print(f'Что-то пошло не так: {e}')
        return False


async def hourly_task():
    while True:
        try:
            data = await db.look_at_dates_of_reminders()
            if not data:
                print('Нет дат для напоминаний, уснул на 1 минуту')
                await asyncio.sleep(60)
                continue
        
            nearest = min(map(lambda x: (x[0], datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S'), x[2], x[3]), data), key=lambda x: x[1])

            difference:timedelta = nearest[1] - datetime.now()
            difference_total_seconds = difference.total_seconds()

            if difference_total_seconds > 60:
                print('Уснул на 1 минуту')
                await asyncio.sleep(60)
                continue

            chat_ids, heading = await db.send_notification(nearest[-1])
            
            if await send_message(chat_ids, heading, *nearest):
                print('Все прошло успешно')
                continue
            
            print('Что-то пошло не так при отправке уведомления')
    
        except Exception as e:
            print(f'Ошибка при отправке уведомления {e}')


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