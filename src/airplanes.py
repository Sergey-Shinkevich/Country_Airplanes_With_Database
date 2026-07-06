from typing import Any, Optional


class Airplane:
    def __init__(self, icao24: str, country: str, callsign: str, velocity: float):

        # ICAO24 - уникальный ключ
        self.icao24 = icao24

        # Страна теперь будет приходить от Nominatim
        self.country = country

        # Валидация позывного
        if callsign is None or str(callsign).strip() == "":
            self.callsign = str(icao24)[0:3] + str(country)
        else:
            self.callsign = callsign

        # Валидация скорости
        self.velocity = float(velocity) if velocity is not None else 0.0


    @classmethod
    def from_api(cls, state: list, country_name: str) -> Optional['Airplane']:
        """
        Передаем country_name принудительно, так как мы сами выбираем страну через Nominatim.
        """
        if not state or len(state) < 10:
            return None
        return cls(
            icao24=str(state[0]),
            country=country_name,  # Берем страну из того запроса, который сделали
            callsign=state[1],
            velocity=state[9]
        )