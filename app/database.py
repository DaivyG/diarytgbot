#TODO сделать отпрваыку пользователям по способу который выберет заказчик
#Также нужно сделать форматирование даты и времени события
from datetime import datetime, timedelta
import sqlite3 as sq

async def date_to_format(event_date):
    now = datetime.now()

    if not event_date:
        next_day = now + timedelta(days=1)
        return [next_day.replace(hour=9, minute=0, second=0, microsecond=0).strftime('%d.%m.%Y %H:%M')]

    event_date = datetime.strptime(event_date, '%d.%m.%Y %H:%M')
    difference = event_date - now

    if difference <= timedelta():
        return None

    reminders = []
    if difference.days >= 7:
        reminders.append(event_date - timedelta(days=7))
    if difference.days >= 3:
        reminders.append(event_date - timedelta(days=3))
    if difference.days >= 1:
        reminders.append(event_date - timedelta(days=1))
    reminders.append(event_date - timedelta(hours=1))

    return reminders


async def db_start():
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute('''CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        full_text TEXT,
                        heading VARCHAR(30) GENERATED ALWAYS AS (SUBSTR(full_text, 30)),
                        date_of_creating DATETIME DEFAULT CURRENT_TIMESTAMP,
                        author VARCHAR(20))''')

        cur.execute('''CREATE TABLE IF NOT EXISTS recipients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        recipients_name VARCHAR(30),
                        chat_id VARCHAR(20),
                        event_id INT NOT NULL,

                        CONSTRAINT event_id_fk FOREIGN KEY (event_id) REFERENCES events (id))''')
        
        cur.execute('''CREATE TABLE IF NOT EXISTS dates_of_reminders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_datetime DATETIME,
                        frequency VARCHAR(20),
                        event_id INT NOT NULL,
                    
                        CONSTRAINT event_id_fk FOREIGN KEY (event_id) REFERENCES events (id))''')

        conn.commit()

    except Exception as e:
        print(f'Ошибка при создании БД внутри database.py: {e}')

    finally:
        cur.close()
        conn.close()

    
async def create_new_event(data:dict):
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        # Получаем значения из словаря data с возможностью установки значения по умолчанию
        full_text = data.get("text", "")
        author = data.get("author", "")
        frequency = data.get("frequency", "Единично")
        chat_id = data.get("chat_id", "")
        datetime_of_event = await date_to_format(data.get("datetime", ""))

        if datetime_of_event is None:
            raise Exception('Вы ввели дату которая уже прошла')
        
        # Вставляем данные в таблицу events
        cur.execute('''INSERT INTO events (full_text, author) VALUES (?, ?)''',
                    (full_text, author))
        
        event_id = cur.lastrowid

        # Вставляем данные в таблицу dates_of_reminders в зависимости от того, что хранится в переменной
        for i in datetime_of_event:
            cur.execute('''INSERT INTO dates_of_reminders (event_datetime, frequency, event_id)
                        VALUES (?, ?, ?)''', (i, frequency, event_id))
        
        # Вставляем данные в таблицу recipients
        cur.execute('''INSERT INTO recipients (recipients_name, chat_id, event_id)
                    VALUES (?, ?, ?)''', ('-', chat_id, event_id))
        
        conn.commit()

        print('Событие успешно создано')
        return True

    except Exception as e:
        print(f'Ошибка при создании нового мероприятия внутри database.py: {e}')
        return False

    finally:
        cur.close()
        conn.close()