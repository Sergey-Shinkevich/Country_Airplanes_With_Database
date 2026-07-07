import psycopg2


class DBManager:
    def __init__(self, dbname, user, password, host="localhost", port="5432"):
        """Конструктор БД"""
        self.conn_params = {"dbname": dbname, "user": user, "password": password, "host": host, "port": port}

    def _connect(self):
        """Метод соединения"""
        return psycopg2.connect(**self.conn_params)

    def clear_tables(self):
        """Полностью очищает таблицы перед новым сбором"""
        with self._connect() as conn:
            with conn.cursor() as cur:
                # TRUNCATE удаляет все записи, но оставляет структуру таблиц
                # CASCADE нужен, чтобы очистить и связанные таблицы
                cur.execute("TRUNCATE TABLE airplanes, countries RESTART IDENTITY CASCADE;")
                conn.commit()

    def create_tables(self):
        """Создает таблицы, если их нет"""
        query = """
        CREATE TABLE IF NOT EXISTS countries (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS airplanes (
            id SERIAL PRIMARY KEY,
            icao24 VARCHAR(20) UNIQUE NOT NULL,
            callsign VARCHAR(20),
            velocity FLOAT,
            country_id INTEGER REFERENCES countries(id)
        );
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                conn.commit()

    def save_all_airplanes(self, airplanes):
        """Заполнение базы данных"""
        with self._connect() as conn:
            with conn.cursor() as cur:
                for airplane in airplanes:
                    # 1. Получаем ID страны ДЛЯ ТЕКУЩЕГО самолета
                    # INSERT ... ON CONFLICT гарантирует, что страна есть
                    # RETURNING id дает нам ID этой конкретной страны
                    cur.execute(
                        """INSERT INTO countries (name) VALUES (%s) ON CONFLICT (name) 
                        DO UPDATE SET name = EXCLUDED.name RETURNING id;""",
                        (airplane.country,),
                    )
                    country_id = cur.fetchone()[0]

                    # 2. Вставляем самолет, привязывая его к полученному country_id
                    cur.execute(
                        """
                        INSERT INTO airplanes (icao24, callsign, velocity, country_id)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (icao24) DO UPDATE SET 
                        callsign = EXCLUDED.callsign, 
                        velocity = EXCLUDED.velocity,
                        country_id = EXCLUDED.country_id;
                    """,
                        (airplane.icao24, airplane.callsign, airplane.velocity, country_id),
                    )

                conn.commit()

    def get_countries_and_aeroplanes_count(self) -> list:
        """Возвращает список пар: (страна, количество самолетов)"""
        query = """
            SELECT c.name, COUNT(a.id)
            FROM countries c
            LEFT JOIN airplanes a ON c.id = a.country_id
            GROUP BY c.name
            ORDER BY COUNT(a.id) DESC;
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()

    def get_all_airplanes(self) -> list:
        """Возвращает список всех самолетов с названиями их стран"""
        query = """
            SELECT a.icao24, a.callsign, a.velocity, c.name
            FROM airplanes a
            JOIN countries c ON a.country_id = c.id;
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                # Получаем все строки
                rows = cur.fetchall()

                # Превращаем результат в список словарей для удобства
                result = []
                for row in rows:
                    result.append({"icao24": row[0], "callsign": row[1], "velocity": row[2], "country": row[3]})
                return result

    def get_avg_speed(self) -> float:
        """Возвращает среднюю скорость всех самолетов"""
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT AVG(velocity) FROM airplanes;")
                result = cur.fetchone()[0]
                return result if result else 0.0

    def get_aeroplanes_with_higher_speed(self) -> list:
        """Получает список всех самолетов, у которых скорость выше средней"""
        query = """
                    SELECT a.icao24, a.callsign, a.velocity, c.name
                    FROM airplanes a
                    JOIN countries c ON a.country_id = c.id
                    WHERE a.velocity > (SELECT AVG(velocity) FROM airplanes)
                    ORDER BY a.velocity DESC;
                """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                # Возвращаем список словарей
                return [{"icao24": r[0], "callsign": r[1], "velocity": r[2], "country": r[3]} for r in rows]

    def get_aeroplanes_with_keyword(self, keyword: str) -> list:
        """Получает список всех самолетов, в позывном которых есть keyword"""
        query = """
            SELECT a.icao24, a.callsign, a.velocity, c.name
            FROM airplanes a
            JOIN countries c ON a.country_id = c.id
            WHERE a.callsign LIKE %s
            ORDER BY a.callsign;
        """
        search_pattern = f"%{keyword}%"

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (search_pattern,))
                rows = cur.fetchall()

                return [{"icao24": r[0], "callsign": r[1], "velocity": r[2], "country": r[3]} for r in rows]
