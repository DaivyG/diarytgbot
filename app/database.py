#TODO сделать отпрваыку пользователям по способу который выберет заказчик
#Также нужно сделать форматирование даты и времени события
import sqlite3 as sq
import app.functions as func


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
        
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(30),
                    name VARCHAR(30))''')

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
        # Вставляем данные в таблицу events
        cur.execute('''INSERT INTO events (full_text, author) VALUES (?, ?)''',
                    (data['text'], data['author']))
        
        event_id = cur.lastrowid

        # Вставляем данные в таблицу dates_of_reminders в зависимости от того, что хранится в переменной
        for i in func.date_to_format(data.get('datetime')):
            cur.execute('''INSERT INTO dates_of_reminders (event_datetime, frequency, event_id)
                        VALUES (?, ?, ?)''', (i, data['frequency'], event_id))
        
        # Вставляем данные в таблицу recipients
        cur.execute('''INSERT INTO recipients (recipients_name, chat_id, event_id)
                    VALUES (?, ?, ?)''', ('-', data['chat_id'], event_id))
        
        conn.commit()

        print('Событие успешно создано')
        return True

    except Exception as e:
        print(f'Ошибка при создании нового мероприятия внутри database.py: {e}')
        return False

    finally:
        cur.close()
        conn.close()