from typing import Any, Dict, List, Optional
from src.base_api_adapter import BaseApiAdapter


class APIAdapter(BaseApiAdapter):
    """
    Класс для работы с API Nominatim и OpenSky.
    Реализует методы получения координат стран и данных о самолетах.
    """

    def __init__(self) -> None:
        self.__openstreetmap_url = "https://openstreetmap.org"
        self.__opensky_url = "https://opensky-network.org"
        self.coordinate: Optional[List[float]] = None
        self.aeroplanes: List[Dict[str, Any]] = []

    def get_coordinate(self, country: str) -> None:
        """Получает географические координаты страны"""
        headers = {"User-Agent": "AviationApp/1.0"}
        params = {"country": country, "format": "json", "limit": 1}

        try:
            response = self._connect(self.__openstreetmap_url, params=params, headers=headers)
            data = response.json()
            if data:
                self.coordinate = [float(x) for x in data[0].get("boundingbox")]
            else:
                self.coordinate = None
        except Exception as e:
            print(f"Ошибка при получении координат {country}: {e}")
            self.coordinate = None

    def get_airplanes(self) -> None:
        """Получает данные о самолетах в текущих координатах"""
        if not self.coordinate:
            print("Сначала необходимо получить координаты страны.")
            return

        params = {
            "lamin": self.coordinate[0],
            "lamax": self.coordinate[1],
            "lomin": self.coordinate[2],
            "lomax": self.coordinate[3],
        }

        try:
            response = self._connect(self.__opensky_url, params=params)
            data = response.json()
            states = data.get("states")

            self.aeroplanes = []
            if states:
                for s in states:
                    self.aeroplanes.append({
                        "icao24": s[0],
                        "callsign": s[1].strip() if s[1] else "Unknown",
                        "origin_country": s[2],
                        "velocity": s[9],
                        "altitude": s[7]
                    })
        except Exception as e:
            print(f"Ошибка при получении данных OpenSky: {e}")
            self.aeroplanes = []
