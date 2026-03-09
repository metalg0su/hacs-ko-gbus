"""버스도착정보 API 실제 호출 테스트."""

import aiohttp
import pytest

from custom_components.kr_gbus.api import BusArrivalApiClient

STATION_ID = "228000704"
ROUTE_ID = "234000016"
STA_ORDER = "5"


@pytest.fixture
async def client(api_key):
    async with aiohttp.ClientSession() as session:
        yield BusArrivalApiClient(service_key=api_key, session=session)


async def test_get_bus_arrival_list(client):
    """getBusArrivalListv2 실제 응답을 파싱한다."""
    resp = await client.async_get_bus_arrival_list(station_id=STATION_ID)
    print(f"\n{resp}")


async def test_get_bus_arrival_item(client):
    """getBusArrivalItemv2 실제 응답을 파싱한다."""
    resp = await client.async_get_bus_arrival_item(
        station_id=STATION_ID,
        route_id=ROUTE_ID,
        sta_order=STA_ORDER,
    )
    print(f"\n{resp}")
