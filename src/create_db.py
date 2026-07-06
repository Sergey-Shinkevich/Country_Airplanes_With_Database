import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import os

def create_database():
    # Подключаемся к системной базе 'postgres'
    load_dotenv()
    DB_KEY = os.getenv("DB_PASS")
    conn = psycopg2.connect(dbname='postgres', user='postgres', password=DB_KEY, host='localhost')
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # Создаем новую базу
    cur.execute('CREATE DATABASE airplane_db')

    cur.close()
    conn.close()
    print("База данных 'airplane_db' успешно создана!")


if __name__ == "__main__":
    create_database()