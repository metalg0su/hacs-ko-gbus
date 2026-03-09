"""정류소 조회 API 실제 호출 테스트."""

import aiohttp
import pytest

from custom_components.kr_gbus.api import BusStationApiClient

STATION_ID = "228000704"
KEYWORD = "버스"
X = "127.0"
Y = "37.5"


@pytest.fixture
async def client(api_key):
    async with aiohttp.ClientSession() as session:
        yield BusStationApiClient(service_key=api_key, session=session)


async def test_get_bus_station_list(client):
    """getBusStationListv2 실제 응답을 파싱한다."""
    resp = await client.async_get_bus_station_list(keyword=KEYWORD)
    print(f"\n{resp}")


async def test_get_bus_station_around_list(client):
    """getBusStationAroundListv2 실제 응답을 파싱한다."""
    resp = await client.async_get_bus_station_around_list(x=X, y=Y)
    print(f"\n{resp}")


async def test_get_bus_station_via_route_list(client):
    """getBusStationViaRouteListv2 실제 응답을 파싱한다."""
    resp = await client.async_get_bus_station_via_route_list(station_id=STATION_ID)
    print(f"\n{resp}")


async def test_get_bus_station_info(client):
    """busStationInfov2 실제 응답을 파싱한다."""
    resp = await client.async_get_bus_station_info(station_id=STATION_ID)
    print(f"\n{resp}")
