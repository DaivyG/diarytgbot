#TODO сделать отпрваыку пользователям по способу который выберет заказчик
#Также нужно сделать форматирование даты и времени события
import sqlite3 as sq
import app.functions as func
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='logfile.log')
logger = logging.getLogger(__name__)

async def db_start():
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute('''CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        full_text TEXT,
                        heading VARCHAR(30) GENERATED ALWAYS AS (SUBSTR(full_text, 0, 30)),
                        date_of_creating DATETIME DEFAULT CURRENT_TIMESTAMP,
                        author VARCHAR(20))''')

        cur.execute('''CREATE TABLE IF NOT EXISTS recipients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        author_name VARCHAR(30),
                        recipient_name VARCHAR(30),
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
        for user in data['recipients']:
            cur.execute('''INSERT INTO recipients (author_name, recipient_name, event_id)
                        VALUES (?, ?, ?)''', (data['author'], user.lower(), event_id))

        conn.commit()

        print('Событие успешно создано')
        return True

    except Exception as e:
        print(f'Ошибка при создании нового мероприятия внутри database.py: {e}')
        return False

    finally:
        cur.close()
        conn.close()


async def look_at_db_users():
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute('SELECT * FROM users')

        data = cur.fetchall()

        if data:
            return list(data)

    except Exception as e:
        print(f'Ошибка {e}')

    finally:
        cur.close()
        conn.close()

    
async def add_at_db_users(data):
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute('''INSERT INTO users (username, name) 
                    VALUES (?, ?)''', (data['username'], data['name']))

        conn.commit()

    except Exception as e:
        print(f'Ошибка {e}')

    finally:
        cur.close()
        conn.close()


async def del_from_db_users(data):
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute(f'DELETE FROM users WHERE name="{data["name"]}"')

        conn.commit()

    except Exception as e:
        print(f'Ошибка {e}')

    finally:
        cur.close()
        conn.close()


async def look_at_db_events(name):
    conn = sq.connect('tg.db')
    cur = conn.cursor()
    try:
        # Выполняем запрос к таблице users
        cur.execute('SELECT name FROM users WHERE username=?', (name,))
        user_name = cur.fetchone()

        if user_name:
            # Если пользователь найден, выполняем запрос к таблице events
            cur.execute('''SELECT heading 
                            FROM events e
                            JOIN recipients r ON e.id = r.event_id
                            WHERE r.recipient_name=?''', (user_name[0],))
            data = cur.fetchall()

            if data:
                return data
            else:
                return 'У вас нет напоминаний'
        else:
            return 'Пользователь не найден'

    except Exception as e:
        print(f'Ошибка {e}')
        return 'Произошла ошибка при выполнении запроса'
    

async def username_to_name(username):
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute('SELECT name FROM users WHERE username=?', (username,))
        user_name = cur.fetchone()

        return user_name[0]

    except Exception as e:
        print(f'Ошибка {e}')

    finally:
        cur.close()
        conn.close()

    
async def look_at_cur_event(event_name):
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute('''SELECT * 
                    FROM events 
                    WHERE heading=?''', (event_name,))

        data = cur.fetchall()
        if data:
            event_id = data[0][0]  # Первый столбец возвращаемого результата, предполагая, что это id

            cur.execute('''SELECT recipient_name
                        FROM recipients
                        WHERE event_id=?''', (event_id,))

            recipients = cur.fetchall()
            return data, recipients

        else:
            return None, None

    except Exception as e:
        print(f'Ошибка {e}')

    finally:
        cur.close()
        conn.close()