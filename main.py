import asyncio
import schedule

from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router
from app import database as db
from datetime import datetime, timedelta

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


async def send_message(chat_ids, period, heading, _id):
    try:
        for chat_id in chat_ids:
            await bot.send_message(chat_id, f'До события {heading} осталось {period}')
        
        '''
        Вместо простого удаления нужно сделать чтобы информация переносилась в выполненные события, и в зависимости от цикличности менялась дата
        '''
        await db.delete_my_event(_id)
        return True

    except Exception as e:
        print(f'Что-то пошло не так: {e}')


async def hourly_task():
    while True:
        try:
            data = await db.look_at_dates_of_reminders()
            if len(data) == 0:
                print('Нет дат для напоминаний, уснул на 3 минуты')
                await asyncio.sleep(60 * 3)
        
            nearest = min(map(lambda x: (x[0], datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S'), x[2], x[3]), data), key=lambda x: x[1])

            difference:timedelta = nearest[1] - datetime.now()
            difference_total_seconds = difference.total_seconds()

            if difference_total_seconds > 3600:
                print('Уснул на час')
                await asyncio.sleep(60 * 60)

            elif difference_total_seconds > 1800 and difference_total_seconds <= 3600:
                print('Уснул на 30 минут')
                await asyncio.sleep(60 * 30)

            else:
                if difference_total_seconds > 60:
                    print('Уснул на 30 sek')
                    print(difference_total_seconds)
                    await asyncio.sleep(30)

                chat_ids, heading = await db.send_notification(nearest[-1])
                period = nearest[0]
                
                print(chat_ids, period, heading)
                await send_message(chat_ids, period, heading, nearest[-1])
    
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