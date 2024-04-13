#TODO сделать отпрваыку пользователям по способу который выберет заказчик
import sqlite3 as sq
import app.functions as func

from datetime import datetime

async def db_start():
    '''
    Создание таблиц в базе данных
    '''
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute('''CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        full_text TEXT,
                        heading VARCHAR(30) GENERATED ALWAYS AS (SUBSTR(full_text, 0, 30)),
                        date_of_creating DATETIME,
                        author VARCHAR(20),
                        date_and_time DATETIME)''')

        cur.execute('''CREATE TABLE IF NOT EXISTS recipients (
                        author_name VARCHAR(30),
                        recipient_name VARCHAR(30),
                        event_id INT NOT NULL,

                        CONSTRAINT event_id_fk FOREIGN KEY (event_id) REFERENCES events (id))''')

        cur.execute('''CREATE TABLE IF NOT EXISTS dates_of_reminders (
                        period VARCHAR(20),
                        event_datetime DATETIME,
                        frequency VARCHAR(20),
                        event_id INT NOT NULL,
                        id INTEGER PRIMARY KEY AUTOINCREMENT,

                        CONSTRAINT event_id_fk FOREIGN KEY (event_id) REFERENCES events (id))''')
        
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username VARCHAR(30),
                        name VARCHAR(30),
                        chat_id VARCHAR(40))''')

        conn.commit()

    except Exception as e:
        print(f'Ошибка при создании БД внутри database.py: {e}')

    finally:
        cur.close()
        conn.close()

    
async def create_new_event(data:dict):
    '''
    Создание нового события
    '''
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        # Вставляем данные в таблицу events
        _datetime = data.get('datetime')
        if _datetime is None:
            _datetime = func.next_day_foo()
        cur.execute('''INSERT INTO events (full_text, date_of_creating, author, date_and_time) VALUES (?, ?, ?, ?)''',
                    (data['text'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'), data['author'], _datetime))

        event_id = cur.lastrowid
        # Вставляем данные в таблицу dates_of_reminders в зависимости от того, что хранится в переменной
        for k, v in func.date_to_format(_datetime, data.get('reminders')).items():
            cur.execute('''INSERT INTO dates_of_reminders (period, event_datetime, frequency, event_id)
                        VALUES (?, ?, ?, ?)''', (k, v, data['frequency'], event_id))

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
    '''
    Просмотр таблицы пользователей
    '''
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute('SELECT * FROM users')

        data = cur.fetchall()

        if data:
            return data

    except Exception as e:
        print(f'Ошибка {e}')

    finally:
        cur.close()
        conn.close()

    
async def add_at_db_users(data):
    '''
    Добавление пользователя в БД
    '''
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute('''INSERT INTO users (username, name, chat_id)
                    VALUES (?, ?, ?)''', (data['username'], data['name'], data.get('chat_id', 'Еще не регистрировался')))

        conn.commit()
        return True

    except Exception as e:
        print(f'Ошибка {e}')
        return False

    finally:
        cur.close()
        conn.close()


async def del_from_db_users(data):
    '''
    Удаление пользователя из БД
    '''
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        for i in data:
            cur.execute(f'DELETE FROM users WHERE name=?', (i,))

        conn.commit()
        return True
    
    except Exception as e:
        print(f'Ошибка {e}')
        return False

    finally:
        cur.close()
        conn.close()


async def look_at_db_events(name):
    '''
    Просмотр всех событий
    '''
    conn = sq.connect('tg.db')
    cur = conn.cursor()
    try:
        # Выполняем запрос к таблице users
        cur.execute('SELECT name FROM users WHERE username=?', (name,))
        user_name = cur.fetchone()

        if user_name:
            # Если пользователь найден, выполняем запрос к таблице events
            cur.execute('''SELECT heading, id
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
    '''
    Функция для преобразования username в имя
    '''
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

    
async def look_at_cur_event(id):
    '''
    Просмотр информации о конкретном событии
    '''
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute('''SELECT *
                    FROM events 
                    WHERE id=?''', (id,))

        data = cur.fetchall()
        if data:
            event_id = data[0][0]  # Первый столбец возвращаемого результата, предполагая, что это id

            cur.execute('''SELECT recipient_name
                        FROM recipients
                        WHERE event_id=?''', (event_id,))

            recipients = cur.fetchall()

            cur.execute('''SELECT frequency
                        FROM dates_of_reminders
                        WHERE event_id=?''', (event_id, ))
            
            frequency = cur.fetchall()[0][0]
            return data, recipients, frequency

        else:
            return None

    except Exception as e:
        print(f'Ошибка {e}')

    finally:
        cur.close()
        conn.close()


async def change_full_text(text, id_):
    '''
    Смена полного текста конкретного события
    '''
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute(f'''UPDATE events SET
                    full_text = ?
                    WHERE id = ?''', (text, id_))
        
        conn.commit()

    except Exception as e:
        print(f'Ошибка {e}')
        return False
    
    finally:
        cur.close()
        conn.close()


async def change_datetime(datetime, id_):
    '''
    Смена даты и времении события
    '''
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute('''UPDATE events 
                    SET date_and_time = ?
                    WHERE id = ?''', (datetime, id_))
       
        cur.execute('''SELECT frequency
                    FROM dates_of_reminders
                    WHERE event_id = ?''', (id_,))
       
        frequency = cur.fetchall()[0][0]

        cur.execute('''DELETE FROM dates_of_reminders
                    WHERE event_id = ?''', (id_,))
       
        list_of_dates_reminders = func.date_to_format(datetime).items()
    
        for k, v in list_of_dates_reminders:
            cur.execute('''INSERT INTO dates_of_reminders (period, event_datetime, frequency, event_id)
                        VALUES (?, ?, ?, ?)''', (k, v, frequency, id_))

        conn.commit()
        return True
    except Exception as e:
        print(f'Ошибка {e}')
        return False

    finally:
        cur.close()
        conn.close()

    
async def change_frequency(frequency, id_):
    '''
    Смена цикличности события
    '''
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute(f'''UPDATE dates_of_reminders
                    SET frequency = ?
                    WHERE event_id = ?''', (frequency, id_))

        conn.commit()
        return True
    
    except Exception as e:
        print(f'Ошибка {e}')
        return False

    finally:
        cur.close()
        conn.close()


async def edit_recipients(author, list_of_users, id_):
    '''
    Смена получателей события
    '''
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute(f'''DELETE FROM recipients
                    WHERE event_id = ?''', (id_,))
        
        for user in list_of_users:
            cur.execute('''INSERT INTO recipients (author_name, recipient_name, event_id)
                        VALUES (?, ?, ?)''', (author, user.lower(), id_))

        conn.commit()
        return True
    
    except Exception as e:
        print(f'Ошибка {e}')
        return False

    finally:
        cur.close()
        conn.close()


async def delete_my_event(id_):
    '''
    Удаление события
    '''
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute(f'''DELETE FROM events
                    WHERE id = ?''', (id_,))
        
        cur.execute(f'''DELETE FROM dates_of_reminders
                    WHERE event_id = ?''', (id_,))
        
        cur.execute(f'''DELETE FROM recipients
                    WHERE event_id = ?''', (id_,))

        conn.commit()
        return True
    
    except Exception as e:
        print(f'Ошибка {e}')
        return False

    finally:
        cur.close()
        conn.close()


async def look_at_dates_of_reminders():
    '''
    Просмотр дат и цикличности напоминаний к разным событиям
    '''
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute('''SELECT * 
                    FROM dates_of_reminders''')
        
        data = cur.fetchall()
        return data
    
    except Exception as e:
        print(f'Ошибка {e}')
        return False

    finally:
        cur.close()
        conn.close()


async def send_notification(event_id):
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute('''SELECT heading
                    FROM events
                    WHERE id = ?''', (event_id,))
        
        heading = cur.fetchall()[0][0]

        cur.execute('''SELECT recipient_name
                    FROM recipients
                    WHERE event_id = ?''', (event_id,))
        
        data = cur.fetchall()
        data = [i[0] for i in data]

        cur.execute(f'''SELECT chat_id
                    FROM users
                    WHERE name IN ({', '.join(['?']*len(data))})''', data)
        
        chat_ids = cur.fetchall()
        chat_ids = [i[0] for i in chat_ids]
        return chat_ids, heading
    
    except Exception as e:
        print(f'Ошибка {e}')
        return False

    finally:
        cur.close()
        conn.close()


async def add_chat_id_at_db_users(username, chat_id):
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute('''UPDATE users
                    SET chat_id = ?
                    WHERE username = ?''', (chat_id, username))
        
        conn.commit()
        return True
    
    except Exception as e:
        print(f'Ошибка {e}')
        return False

    finally:
        cur.close()
        conn.close()


async def del_date_of_reminder(id_):
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        cur.execute('''DELETE FROM dates_of_reminders
                    WHERE id = ?''', (id_,))
        
        conn.commit()
        return True
    
    except Exception as e:
        print(f'Ошибка {e}')
        return False

    finally:
        cur.close()
        conn.close()


async def change_date_of_reminder(new_datetime, id_):
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        print(new_datetime)
        cur.execute('''UPDATE dates_of_reminders
                    SET event_datetime = ?
                    WHERE id = ?''', (new_datetime, id_))
        
        conn.commit()
        return True
    
    except Exception as e:
        print(f'Ошибка {e}')
        return False

    finally:
        cur.close()
        conn.close()


async def change_reminders(_datetime, list_of_reminders, frequency, _id):
    conn = sq.connect('tg.db')
    cur = conn.cursor()

    try:
        if list_of_reminders is False:
            return None
        
        cur.execute('''DELETE FROM dates_of_reminders
                    WHERE event_id = ?''', (_id,))

        for k, v in func.date_to_format(_datetime, list_of_reminders).items():
            cur.execute('''INSERT INTO dates_of_reminders (period, event_datetime, frequency, event_id)
                        VALUES (?, ?, ?, ?)''', (k, v, frequency, _id))
            
        conn.commit()
        return True

    except Exception as e:
        print(f'Ошибка {e}')
        return False

    finally:
        cur.close()
        conn.close()