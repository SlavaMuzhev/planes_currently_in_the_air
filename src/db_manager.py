from typing import Any, Dict, List

import psycopg2


class DBManager:
    """Класс для управления данными в БД PostgreSQL."""

    def __init__(self, db_params: Dict[str, Any]) -> None:
        self.conn = psycopg2.connect(**db_params)
        self.conn.autocommit = True

    def create_tables(self) -> None:
        """Создает необходимые таблицы."""
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS countries (
                    id SERIAL PRIMARY KEY, name VARCHAR(100),
                    lat_min FLOAT, lat_max FLOAT, lon_min FLOAT, lon_max FLOAT
                );
                CREATE TABLE IF NOT EXISTS aeroplanes (
                    id SERIAL PRIMARY KEY, icao24 VARCHAR(20), callsign VARCHAR(20),
                    origin_country VARCHAR(100), velocity FLOAT, altitude FLOAT,
                    country_id INTEGER REFERENCES countries(id) ON DELETE CASCADE
                );
            """)

    def truncate_tables(self) -> None:
        """Очищает данные из всех таблиц и сбрасывает счетчики ID"""
        with self.conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE countries, aeroplanes RESTART IDENTITY CASCADE;")
            print("Таблицы успешно очищены.")

    def insert_data(self, country_name: str, coords: List[float], planes: List[Dict[str, Any]]) -> None:
        """Заполняет таблицы данными."""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO countries (name, lat_min, lat_max, lon_min, lon_max)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            """,
                (country_name, *coords),
            )
            country_id = cur.fetchone()[0]

            for p in planes:
                cur.execute(
                    """
                    INSERT INTO aeroplanes (icao24, callsign, origin_country, velocity, altitude, country_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """,
                    (p["icao24"], p["callsign"], p["origin_country"], p["velocity"], p["altitude"], country_id),
                )

    def get_countries_and_aeroplanes_count(self) -> List[Any]:
        """Получает список всех стран и количество самолетов в их воздушных пространствах"""
        query = """
            SELECT countries.name, COUNT(aeroplanes.id)
            FROM countries LEFT JOIN aeroplanes ON countries.id = aeroplanes.country_id
            GROUP BY countries.name
            """
        return self._execute_select(query)

    def get_all_aeroplanes(self) -> List[Any]:
        """Получает список всех воздушных судов"""
        return self._execute_select("SELECT * FROM aeroplanes")

    def get_avg_speed(self) -> float:
        """Получает среднюю скорость по самолетам."""
        with self.conn.cursor() as cur:
            cur.execute("SELECT AVG(velocity) FROM aeroplanes")
            result = cur.fetchone()
            if result and result[0] is not None:
                return float(result[0])
            return 0.0

    def get_aeroplanes_with_higher_speed(self) -> List[Any]:
        """Получает список всех самолетов, у которых скорость выше средней."""
        query = "SELECT * FROM aeroplanes WHERE velocity > (SELECT AVG(velocity) FROM aeroplanes)"
        return self._execute_select(query)

    def get_aeroplanes_with_keyword(self, keyword: str) -> List[Any]:
        """Получает список всех самолетов, в позывном которых содержатся переданные в метод символы."""
        query = "SELECT * FROM aeroplanes WHERE callsign LIKE %s"
        with self.conn.cursor() as cur:
            cur.execute(query, (f"%{keyword}%",))
            result = cur.fetchall()
            return list(result)

    def _execute_select(self, query: str) -> List[Any]:
        with self.conn.cursor() as cur:
            cur.execute(query)
            result = cur.fetchall()
            return list(result)

    def close(self) -> None:
        """Закрывает соединение с БД"""
        self.conn.close()
