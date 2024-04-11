import asyncio

from aiogram import Bot, Dispatcher
from config import TOKEN
from app.handlers import router
from app import database as db
from datetime import datetime, timedelta
from aiogram.client.bot import DefaultBotProperties

bot = Bot(TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
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


async def send_message(chat_ids, heading, period, datetime_of_event:datetime, frequency, _id):
    try:
        for chat_id in chat_ids:
            await bot.send_message(chat_id, [f'До события {heading} осталось {period}', f'Событие {heading} только что наступило'][period == 'Сейчас'])
        
        if period == 'Сейчас':
            if frequency == 'Единично':
                await db.delete_my_event(_id)
                await bot.send_message(chat_id, 'Единичное событие удалено')
            elif frequency == 'Ежедневно':
                await db.change_datetime(str(datetime_of_event.replace(day=datetime_of_event.day + 1).strftime('%d.%m.%Y %H:%M')), _id)
                await bot.send_message(chat_id, 'Событие перенесено на следующий день')
            elif frequency == 'Еженедельно':
                await db.change_datetime(str(datetime_of_event.replace(day=datetime_of_event.day + 7).strftime('%d.%m.%Y %H:%M')), _id)
                await bot.send_message(chat_id, 'Событие перенесно на следующую неделю')
            elif frequency == 'Ежемесячно':
                await db.change_datetime(str(datetime_of_event.replace(month=datetime_of_event.month + 1).strftime('%d.%m.%Y %H:%M')), _id)
                await bot.send_message(chat_id, 'Событие перенесено на следующий месяц')
            elif frequency == 'Ежегодно':
                await db.change_datetime(str(datetime_of_event.replace(year=datetime_of_event.year + 1).strftime('%d.%m.%Y %H:%M')), _id)
                await bot.send_message(chat_id, 'Событие перенесено на следующий год')
        return True
            
        # await db.delete_my_event(_id)
        # return True

    except Exception as e:
        print(f'Что-то пошло не так: {e}')
        return False


async def hourly_task():
    while True:
        try:
            data = await db.look_at_dates_of_reminders()
            if not data:
                print('Нет даты для напоминаний, уснул на 30 минут')
                await asyncio.sleep(60 * 30)
                continue
        
            nearest = min(map(lambda x: (x[0], datetime.strptime(x[1], '%Y-%m-%d %H:%M:%S'), x[2], x[3]), data), key=lambda x: x[1])

            difference:timedelta = nearest[1] - datetime.now()
            difference_total_seconds = difference.total_seconds()

            if difference_total_seconds > 60 * 10:
                print('Есть напоминания, уснул на 1 минут')
                await asyncio.sleep(60)
                continue
            
            else:
                chat_ids, heading = await db.send_notification(nearest[-1])
                
                if await send_message(chat_ids, heading, *nearest):
                    print('Все прошло успешно')
                    continue
                else:
                    print('Что-то пошло не так при отправке уведомления')
                    continue
                
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