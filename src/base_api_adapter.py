from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import requests


class BaseApiAdapter(ABC):
    """
    Абстрактный класс для работы с API сервисов
    для получения географические координаты стран
    и информации о самолетах
    """

    @abstractmethod
    def get_coordinate(self, country: str) -> None:
        pass

    @abstractmethod
    def get_airplanes(self) -> None:
        pass

    def _connect(
        self, url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """
        Метод подключения с проверкой статус-кода
        """
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response
