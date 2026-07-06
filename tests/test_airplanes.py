from src.airplanes import Airplane


def test_airplanes_init_full() -> None:
    """Проверка корректной инициализации со всеми данными"""
    plane = Airplane("123456", "Canada", "ACA123", 500.0)
    assert plane.icao24 == "123456"
    assert plane.callsign == "ACA123"
    assert plane.velocity == 500.0


def test_airplanes_init_missing_callsign() -> None:
    """Проверка создания позывного, если передан None"""
    # 123 + Canada = "123Canada"
    plane = Airplane("123456", "Canada", None, 500.0)
    assert plane.callsign == "123Canada"


def test_airplanes_init_none_values() -> None:
    """Проверка инициализации при отсутствии скорости и высоты"""
    plane = Airplane("123", "USA", "A1", None)
    assert plane.velocity == 0.0


def test_from_api_success() -> None:
    """Проверка создания объекта из данных API"""
    # Создаем список с достаточным количеством элементов, чтобы индекс [9] существовал
    # Индексы: 0=icao, 1=callsign, 9=velocity
    raw_data = ["icao1"] + [None] * 8 + [500.0]

    plane = Airplane.from_api(raw_data, "Germany")

    assert isinstance(plane, Airplane)
    assert plane.icao24 == "icao1"
    assert plane.velocity == 500.0


def test_from_api_invalid_data() -> None:
    """Проверка, что метод возвращает None при плохих данных"""
    # Нужно передать страну, так как это обязательный аргумент
    assert Airplane.from_api([], "Germany") is None
    assert Airplane.from_api(["short"], "Germany") is None

