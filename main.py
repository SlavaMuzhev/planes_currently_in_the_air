import os

from dotenv import load_dotenv

from src.api import APIAdapter
from src.db_manager import DBManager


def main() -> None:
    load_dotenv()

    db_params = {
        "database": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
    }

    adapter = APIAdapter()
    db = DBManager(db_params)

    countries = ["Russia", "Germany", "France", "China", "USA", "Italy", "Japan", "Spain", "Turkey", "Canada"]

    try:
        print("--- Подготовка базы данных ---")
        db.create_tables()
        db.truncate_tables()  # Очищаем перед началом

        print("\n--- Сбор данных из API (это может занять время) ---")
        for country_name in countries:
            print(f"Обработка: {country_name}...")

            # Получаем координаты страны
            adapter.get_coordinate(country_name)

            if adapter.coordinate:
                # Получаем самолеты в этой зоне
                adapter.get_airplanes()

                # Загружаем всё в БД
                db.insert_data(country_name, adapter.coordinate, adapter.aeroplanes)
                print(f"   Найдено и сохранено самолетов: {len(adapter.aeroplanes)}")
            else:
                print(f"   Не удалось получить координаты для {country_name}")

        print("\n--- Выполнение аналитических запросов ---")

        # 1. Список стран и количество самолетов
        print("\nКоличество самолетов по странам:")
        for row in db.get_countries_and_aeroplanes_count():
            print(f"Страна: {row[0]}, Самолетов: {row[1]}")

        # 2. Средняя скорость
        avg_speed = db.get_avg_speed()
        print(f"\nСредняя скорость всех самолетов: {avg_speed:.2f} м/с")

        # 3. Самолеты со скоростью выше средней
        high_speed_planes = db.get_aeroplanes_with_higher_speed()
        print(f"Количество самолетов быстрее среднего: {len(high_speed_planes)}")

        # 4. Поиск по ключевому слову
        keyword = "ACA"
        keyword_planes = db.get_aeroplanes_with_keyword(keyword)
        print(f"\nСамолеты с позывным, содержащим '{keyword}': {len(keyword_planes)}")
        for plane in keyword_planes[:5]:  # Показываем первые 5 для примера
            print(f"   - ИКАО: {plane[1]}, Позывной: {plane[2]}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        db.close()
        print("\nСоединение с БД закрыто.")


if __name__ == "__main__":
    main()
