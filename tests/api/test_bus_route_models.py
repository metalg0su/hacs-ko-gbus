"""버스노선 조회 API 실제 호출 테스트."""

import aiohttp
import pytest

from custom_components.kr_gbus.api import BusRouteApiClient

ROUTE_ID = "234000016"
KEYWORD = "5100"


@pytest.fixture
async def client(api_key):
    async with aiohttp.ClientSession() as session:
        yield BusRouteApiClient(service_key=api_key, session=session)


async def test_get_bus_route_info_item(client):
    """getBusRouteInfoItemv2 실제 응답을 파싱한다."""
    resp = await client.async_get_bus_route_info_item(route_id=ROUTE_ID)
    print(f"\n{resp}")


async def test_get_bus_route_list(client):
    """getBusRouteListv2 실제 응답을 확인한다."""
    resp = await client.async_get_bus_route_list(keyword=KEYWORD)
    print(f"\n{resp}")
