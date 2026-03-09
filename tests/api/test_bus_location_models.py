"""버스위치정보 조회 API 실제 호출 테스트."""

import aiohttp
import pytest

from custom_components.kr_gbus.api import BusLocationApiClient

ROUTE_ID = "234000016"


@pytest.fixture
async def client(api_key):
    async with aiohttp.ClientSession() as session:
        yield BusLocationApiClient(service_key=api_key, session=session)


async def test_get_bus_location_list(client):
    """getBusLocationListv2 실제 응답을 파싱한다."""
    resp = await client.async_get_bus_location_list(route_id=ROUTE_ID)
    print(f"\n{resp}")
