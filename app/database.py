import sqlite3 as sq

conn = sq.connect('tg.db')
cur = conn.cursor()

async def db_start():
    try:
        cur.execute('''CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        full_text TEXT,
                        short_name VARCHAR(30) GENERATED ALWAYS AS (SUBSTR(full_text, 30)),
                        date_of_creating DATETIME DEFAULT CURRENT_TIMESTAMP,
                        author VARCHAR(30))''')

        cur.execute('''CREATE TABLE IF NOT EXISTS recipients (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        recipient_name VARCHAR(30),
                        event_id INT NOT NULL,

                        CONSTRAINT event_id_fk FOREIGN KEY (event_id) REFERENCES events (id))''')
        
        cur.execute('''CREATE TABLE IF NOT EXISTS dates_of_reminders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        event_datetime DATETIME,
                        event_id INT NOT NULL,
                    
                        CONSTRAINT event_id_fk FOREIGN KEY (event_id) REFERENCES events (id))''')

        conn.commit()

    except Exception as e:
        print(f'Ошибка при создании БД внутри датабаз: {e}')

    finally:
        cur.close()
        conn.close()