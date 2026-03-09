"""API 키 검증."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from ...api import BusArrivalApiClient, BusStationApiClient


async def validate_api_key(
    hass: HomeAssistant, service_key: str
) -> None:
    """API 키를 검증한다.

    하나의 API 키로 arrival, station 클라이언트 모두 동작하는지 확인한다.
    Config Flow 단계에서 검증하는 이유:
    async_setup_entry 전에 잘못된 API 키를 걸러내서,
    사용자에게 즉시 에러를 보여주고 재입력받기 위함.
    """
    session = async_create_clientsession(hass)

    arrival = BusArrivalApiClient(service_key=service_key, session=session)
    await arrival.async_get_bus_arrival_list(station_id="228000704")

    station = BusStationApiClient(service_key=service_key, session=session)
    await station.async_get_bus_station_list(keyword="수원")
