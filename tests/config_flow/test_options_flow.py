"""options flow 테스트."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.kr_gbus.api.client.bus_station_client import (
    BusStationItem,
    BusStationListResponse,
    BusStationViaRouteItem,
    BusStationViaRouteListResponse,
)
from custom_components.kr_gbus.api.exceptions import GBusApiClientCommunicationError
from custom_components.kr_gbus.const import (
    CONF_API_KEY_ARRIVAL,
    CONF_MONITORS,
    CONF_MONITOR_ROUTE_ID,
    CONF_MONITOR_STATION_ID,
    CONF_MONITOR_STA_ORDER,
    DOMAIN,
)

STATION_CLIENT_PATH = (
    "custom_components.kr_gbus.config_flow_handler.options_flow"
    ".BusStationApiClient"
)

MOCK_STATION = BusStationItem(
    centerYn="N",
    mobileNo="01234",
    regionName="수원",
    stationId=228000704,
    stationName="영통역",
    x=127.0,
    y=37.0,
)

MOCK_VIA_ROUTE = BusStationViaRouteItem(
    regionName="수원",
    routeDestId=228000100,
    routeDestName="수원역",
    routeId=228000031,
    routeName="300",
    routeTypeCd=11,
    routeTypeName="직행좌석",
    staOrder=15,
)

EXISTING_MONITOR = {
    CONF_MONITOR_STATION_ID: "228000704",
    CONF_MONITOR_ROUTE_ID: "228000031",
    CONF_MONITOR_STA_ORDER: "15",
    "station_name": "영통역",
    "route_name": "300",
}


@pytest.fixture
def config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """옵션이 비어있는 config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_API_KEY_ARRIVAL: "test_key"},
        options={CONF_MONITORS: []},
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def config_entry_with_monitor(hass: HomeAssistant) -> MockConfigEntry:
    """모니터가 1개 있는 config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_API_KEY_ARRIVAL: "test_key"},
        options={CONF_MONITORS: [dict(EXISTING_MONITOR)]},
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_station_client() -> AsyncMock:
    """BusStationApiClient mock."""
    client = AsyncMock()
    client.async_get_bus_station_list.return_value = BusStationListResponse(
        queryTime="2026-03-29",
        resultCode=0,
        resultMessage="OK",
        busStationList=[MOCK_STATION],
    )
    client.async_get_bus_station_via_route_list.return_value = (
        BusStationViaRouteListResponse(
            queryTime="2026-03-29",
            resultCode=0,
            resultMessage="OK",
            busRouteList=[MOCK_VIA_ROUTE],
        )
    )
    return client


async def test_add_monitor_full_flow(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    mock_station_client: AsyncMock,
) -> None:
    """모니터 추가 전체 플로우: 검색 → 정류장 선택 → 노선 선택 → 저장."""
    with patch(STATION_CLIENT_PATH, return_value=mock_station_client):
        # init → 바로 search_station
        result = await hass.config_entries.options.async_init(
            config_entry.entry_id
        )
        assert result["step_id"] == "search_station"

        # search_station → 키워드 입력
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={"keyword": "영통"},
        )
        assert result["step_id"] == "select_station"

        # select_station → 정류장 선택
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={"station": "228000704"},
        )
        assert result["step_id"] == "select_route"

        # select_route → 노선 선택 → 저장
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={"route": "228000031"},
        )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    monitors = result["data"][CONF_MONITORS]
    assert len(monitors) == 1
    assert monitors[0][CONF_MONITOR_STATION_ID] == "228000704"
    assert monitors[0][CONF_MONITOR_ROUTE_ID] == "228000031"
    assert monitors[0][CONF_MONITOR_STA_ORDER] == "15"
    assert monitors[0]["station_name"] == "영통역"
    assert monitors[0]["route_name"] == "300"


async def test_search_station_no_results(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
) -> None:
    """검색 결과 없으면 no_results 에러를 보여준다."""
    empty_response = BusStationListResponse(
        queryTime="2026-03-29",
        resultCode=0,
        resultMessage="OK",
        busStationList=None,
    )
    mock_client = AsyncMock()
    mock_client.async_get_bus_station_list.return_value = empty_response

    with patch(STATION_CLIENT_PATH, return_value=mock_client):
        result = await hass.config_entries.options.async_init(
            config_entry.entry_id
        )
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={"keyword": "없는정류장"},
        )

    assert result["step_id"] == "search_station"
    assert result["errors"]["base"] == "no_results"


async def test_search_station_api_error(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
) -> None:
    """검색 API 오류 시 connection 에러를 보여준다."""
    mock_client = AsyncMock()
    mock_client.async_get_bus_station_list.side_effect = (
        GBusApiClientCommunicationError
    )

    with patch(STATION_CLIENT_PATH, return_value=mock_client):
        result = await hass.config_entries.options.async_init(
            config_entry.entry_id
        )
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={"keyword": "영통"},
        )

    assert result["step_id"] == "search_station"
    assert result["errors"]["base"] == "connection"


async def test_duplicate_monitor_rejected(
    hass: HomeAssistant,
    config_entry_with_monitor: MockConfigEntry,
    mock_station_client: AsyncMock,
) -> None:
    """이미 등록된 모니터 추가 시 duplicate_monitor 에러를 보여준다."""
    with patch(STATION_CLIENT_PATH, return_value=mock_station_client):
        result = await hass.config_entries.options.async_init(
            config_entry_with_monitor.entry_id
        )
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={"keyword": "영통"},
        )
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={"station": "228000704"},
        )
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={"route": "228000031"},
        )

    assert result["step_id"] == "select_route"
    assert result["errors"]["base"] == "duplicate_monitor"
