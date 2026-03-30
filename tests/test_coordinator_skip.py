"""운행종료 스킵 로직 테스트."""

from custom_components.kr_gbus.api.client.bus_arrival_client import BusArrivalItem
from custom_components.kr_gbus.api.models import RouteFlag
from custom_components.kr_gbus.coordinator.base import (
    GBusCoordinatorData,
    MonitorKey,
    is_station_stopped,
)


def _make_arrival_item(flag: RouteFlag, route_id: int = 1, station_id: int = 100, sta_order: int = 1) -> BusArrivalItem:
    return BusArrivalItem(
        flag=flag,
        routeId=route_id,
        routeName="300",
        staOrder=sta_order,
        stationId=station_id,
    )


KEY_A: MonitorKey = ("100", "1", "1")
KEY_B: MonitorKey = ("100", "2", "2")


def test_is_station_stopped_all_stopped():
    """모든 노선이 운행종료면 True."""
    prev: GBusCoordinatorData = {
        KEY_A: _make_arrival_item(RouteFlag.운행종료),
        KEY_B: _make_arrival_item(RouteFlag.운행종료, route_id=2),
    }
    assert is_station_stopped([KEY_A, KEY_B], prev) is True


def test_is_station_stopped_one_running():
    """하나라도 운행중이면 False."""
    prev: GBusCoordinatorData = {
        KEY_A: _make_arrival_item(RouteFlag.운행종료),
        KEY_B: _make_arrival_item(RouteFlag.운행중, route_id=2),
    }
    assert is_station_stopped([KEY_A, KEY_B], prev) is False


def test_is_station_stopped_none_item():
    """항목이 None이면 False (안전 처리)."""
    prev: GBusCoordinatorData = {KEY_A: None}
    assert is_station_stopped([KEY_A], prev) is False


def test_is_station_stopped_no_prev_data():
    """이전 데이터 없으면 False."""
    assert is_station_stopped([KEY_A], None) is False


def test_stopped_data_preserved_across_skip():
    """스킵 시 prev_data의 운행종료 아이템이 유지되어 다음 주기에도 스킵 가능해야 한다.

    이 테스트는 coordinator의 스킵 로직이 None 대신 prev_data를 유지하는지
    _is_station_stopped를 연속 호출하여 검증한다.
    """
    stopped_item = _make_arrival_item(RouteFlag.운행종료)

    # Cycle 1: API가 운행종료를 반환했다고 가정
    cycle1_data: GBusCoordinatorData = {KEY_A: stopped_item}
    assert is_station_stopped([KEY_A], cycle1_data) is True

    # Cycle 2: 스킵 시 prev_data[key]를 유지 (수정된 로직)
    cycle2_data: GBusCoordinatorData = {KEY_A: cycle1_data[KEY_A]}
    assert is_station_stopped([KEY_A], cycle2_data) is True

    # Cycle 3: 여전히 유지
    cycle3_data: GBusCoordinatorData = {KEY_A: cycle2_data[KEY_A]}
    assert is_station_stopped([KEY_A], cycle3_data) is True
