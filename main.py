import os

from dotenv import load_dotenv

from src.api import AirTrafficAPI
from src.db_manager import DBManager


def main():
    # 1. Инициализация
    load_dotenv()
    api = AirTrafficAPI()
    DB_KEY = os.getenv("DB_PASS")
    db = DBManager(dbname="airplane_db", user="postgres", password=DB_KEY)

    # 2. Создаем таблицы (это нужно сделать один раз)
    db.create_tables()
    db.clear_tables()

    # 3. Список стран из задания
    target_countries = ["United States", "Germany", "United Kingdom", "Japan"]

    # 4. Сбор данных
    print("Начинаю сбор данных...")
    for country in target_countries:
        api.get_data(country)

    # 5. Загрузка в БД
    print(f"Загружаю {len(api.airplanes)} самолетов в БД...")
    db.save_all_airplanes(api.airplanes)  # Вызываем один метод
    print("Данные успешно сохранены!")

    # 6. Проверка работы методов (для демонстрации)
    print("\nСамолетов по странам:")
    for country, count in db.get_countries_and_aeroplanes_count():
        print(f"{country}: {count}")
    print("--------------------------------------------------------")

    all_planes = db.get_all_airplanes()
    for plane in all_planes:
        print(f"Самолет {plane['icao24']} ({plane['country']}): скорость {plane['velocity']} км/ч")
    print("--------------------------------------------------------")

    print(f"Средняя скорость: {db.get_avg_speed():.2f} км/ч")
    print("--------------------------------------------------------")

    print("\n--- Самолеты быстрее среднего ---")
    fast_planes = db.get_aeroplanes_with_higher_speed()
    for plane in fast_planes:
        print(f"{plane['icao24']} ({plane['country']}) — {plane['velocity']} км/ч")
    print("--------------------------------------------------------")

    print("\nПоиск по позывному 'ACA'")
    results = db.get_aeroplanes_with_keyword("ACA")
    for plane in results:
        print(f"Найдено: {plane['callsign']} ({plane['country']})")


if __name__ == "__main__":
    main()
