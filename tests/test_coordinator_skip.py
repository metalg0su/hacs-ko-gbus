"""운행종료 스킵 로직 테스트."""

from datetime import datetime, time

from custom_components.kr_gbus.api.client.bus_arrival_client import BusArrivalItem
from custom_components.kr_gbus.api.client.bus_route_client import BusRouteInfoItem
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


def _make_route_info(
    up_first_time: time | None = None,
    down_last_time: time | None = None,
) -> BusRouteInfoItem:
    return BusRouteInfoItem(
        routeId=1,
        routeName="300",
        upFirstTime=up_first_time,
        downLastTime=down_last_time,
    )


KEY_A: MonitorKey = ("100", "1", "1")
KEY_B: MonitorKey = ("100", "2", "2")

FIRST_BUS = time(5, 30)
LAST_BUS = time(22, 30)
SCHEDULES = {
    "1": _make_route_info(FIRST_BUS, LAST_BUS),
    "2": _make_route_info(FIRST_BUS, LAST_BUS),
}


def test_stopped_before_first_bus():
    """운행종료 + 첫차 이전 → 스킵(True)."""
    prev: GBusCoordinatorData = {
        KEY_A: _make_arrival_item(RouteFlag.운행종료),
    }
    now = datetime(2026, 3, 30, 3, 0)  # 03:00, 첫차(05:30) 이전
    assert is_station_stopped([KEY_A], prev, SCHEDULES, now) is True


def test_stopped_after_first_bus():
    """운행종료 + 첫차 이후 → 호출(False)."""
    prev: GBusCoordinatorData = {
        KEY_A: _make_arrival_item(RouteFlag.운행종료),
    }
    now = datetime(2026, 3, 30, 6, 0)  # 06:00, 첫차(05:30) 이후
    assert is_station_stopped([KEY_A], prev, SCHEDULES, now) is False


def test_one_running():
    """하나라도 운행중이면 False."""
    prev: GBusCoordinatorData = {
        KEY_A: _make_arrival_item(RouteFlag.운행종료),
        KEY_B: _make_arrival_item(RouteFlag.운행중, route_id=2),
    }
    now = datetime(2026, 3, 30, 3, 0)
    assert is_station_stopped([KEY_A, KEY_B], prev, SCHEDULES, now) is False


def test_none_item():
    """항목이 None이면 False (안전 처리)."""
    prev: GBusCoordinatorData = {KEY_A: None}
    now = datetime(2026, 3, 30, 3, 0)
    assert is_station_stopped([KEY_A], prev, SCHEDULES, now) is False


def test_no_schedule_info():
    """스케줄 정보가 없으면 False (안전 처리)."""
    prev: GBusCoordinatorData = {
        KEY_A: _make_arrival_item(RouteFlag.운행종료),
    }
    now = datetime(2026, 3, 30, 3, 0)
    assert is_station_stopped([KEY_A], prev, {}, now) is False


def test_stopped_late_night():
    """운행종료 + 자정 이전 야간 → 스킵(True). 내일 첫차 기준."""
    prev: GBusCoordinatorData = {
        KEY_A: _make_arrival_item(RouteFlag.운행종료),
    }
    now = datetime(2026, 3, 30, 23, 0)  # 23:00, 첫차(05:30) 이미 지남 → 내일 첫차 기준
    assert is_station_stopped([KEY_A], prev, SCHEDULES, now) is True


def test_stopped_data_preserved_across_skip():
    """스킵 시 prev_data가 유지되어 다음 주기에도 스킵 가능해야 한다."""
    stopped_item = _make_arrival_item(RouteFlag.운행종료)
    now = datetime(2026, 3, 30, 3, 0)  # 첫차 이전

    cycle1_data: GBusCoordinatorData = {KEY_A: stopped_item}
    assert is_station_stopped([KEY_A], cycle1_data, SCHEDULES, now) is True

    cycle2_data: GBusCoordinatorData = {KEY_A: cycle1_data[KEY_A]}
    assert is_station_stopped([KEY_A], cycle2_data, SCHEDULES, now) is True
