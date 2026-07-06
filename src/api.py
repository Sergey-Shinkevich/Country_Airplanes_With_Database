from abc import ABC, abstractmethod
from typing import Any, Dict

import requests

from src.airplanes import Airplane


class APIClient(ABC):
    """Абстрактный класс"""

    @abstractmethod
    def connect(self) -> bool:
        """Шаблон метода для проверки связи до API"""
        pass

    @abstractmethod
    def get_data(self, *args: Any, **kwargs: Any) -> Any:
        """Шаблон метода получения данных с API"""
        pass


class AirTrafficAPI(APIClient):
    """Класс получения самолетов на данной территории"""

    def __init__(self) -> None:
        """Метод - конструктор"""
        self.__nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.__opensky_url = "https://opensky-network.org/api/states/all"
        # Список будет накапливать самолеты из всех запрошенных стран
        self.airplanes: list = []

    def connect(self) -> bool:
        """Проверяет доступность API."""
        try:
            headers = {"User-Agent": "MyLearningApp/1.0"}
            response_1 = requests.get(self.__nominatim_url, headers=headers, timeout=5)
            response_2 = requests.get(self.__opensky_url, headers=headers, timeout=5)
            return (response_1.status_code == 200) and (response_2.status_code == 200)
        except requests.exceptions.RequestException:
            return False

    def get_data(self, country: str) -> None:
        """Метод получения самолетов на данной территории"""

        if not self.connect():
            print("Нет соединения с сетью!")
            return
        try:
            # 1. Работа с Nominatim
            headers = {"User-Agent": "test-app"}
            params_nominatim: Dict[str, Any] = {"country": country, "format": "json", "limit": 1}
            response_geo = requests.get(self.__nominatim_url, params=params_nominatim, headers=headers, timeout=10)
            response_geo.raise_for_status()

            geo_data = response_geo.json()
            if not isinstance(geo_data, list) or not geo_data:
                raise ValueError(f"Страна '{country}' не найдена.")

            item = geo_data[0]
            bbox = item.get("boundingbox")
            if not bbox:
                raise ValueError(f"Координаты для '{country}' не найдены.")

            # 2. Работа с OpenSky Network
            params_sky: Dict[str, Any] = {
                "lamin": float(bbox[0]),
                "lamax": float(bbox[1]),
                "lomin": float(bbox[2]),
                "lomax": float(bbox[3]),
            }
            response_sky = requests.get(self.__opensky_url, params=params_sky, timeout=10)
            response_sky.raise_for_status()

            data = response_sky.json()
            states = data.get("states")

            if states:
                new_planes = []
                for s in states:
                    plane = Airplane.from_api(s, country)
                    if plane is not None:
                        new_planes.append(plane)

                self.airplanes.extend(new_planes)

                print(f"[{country}] Добавлено самолетов: {len(new_planes)}")
            else:
                print(f"[{country}] Самолеты на данной территории не найдены.")

        except ValueError as ve:
            print(f"Ошибка данных: {ve}")
        except requests.exceptions.RequestException as e:
            print(f"Сетевая ошибка при запросе страны {country}: {e}")