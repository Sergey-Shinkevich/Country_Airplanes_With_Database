from typing import Any
from unittest.mock import MagicMock, patch

from src.api import AirTrafficAPI


@patch("src.api.AirTrafficAPI.connect")
@patch("src.api.requests.get")
@patch("src.airplanes.Airplane.from_api")
def test_get_data_success(mock_from_api: Any, mock_get: Any, mock_connect: Any) -> None:
    """Тестируем успешный сценарий"""
    mock_connect.return_value = True

    # Имитируем ответ Nominatim
    mock_resp_geo = MagicMock()
    mock_resp_geo.json.return_value = [{"boundingbox": ["1", "2", "3", "4"]}]

    # Имитируем ответ OpenSky
    mock_resp_sky = MagicMock()
    mock_resp_sky.json.return_value = {"states": [["data_for_airplane"]]}

    mock_get.side_effect = [mock_resp_geo, mock_resp_sky]

    # Создаем мок самолета
    mock_plane = MagicMock()
    mock_plane.icao24 = "icao1"

    # Теперь указываем, что from_api принимает ДВА аргумента: state и country
    mock_from_api.return_value = mock_plane

    api = AirTrafficAPI()
    api.get_data("Canada")

    assert len(api.airplanes) == 1
    assert api.airplanes[0].icao24 == "icao1"

    # Проверяем, что метод был вызван с двумя аргументами: данными и названием страны
    mock_from_api.assert_called_once_with(["data_for_airplane"], "Canada")
