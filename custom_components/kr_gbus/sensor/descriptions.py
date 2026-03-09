"""센서 설명 (descriptions)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntityDescription

from ..api.client.bus_arrival_client import BusArrivalItem
from ..api.client.bus_route_client import BusRouteInfoItem
from ..helpers import DayType


@dataclass(frozen=True, kw_only=True)
class GBusSensorEntityDescription(SensorEntityDescription):
    """kr_gbus 센서 설명."""

    value_fn: Callable[[BusArrivalItem], Any]


@dataclass(frozen=True, kw_only=True)
class GBusRouteSensorEntityDescription(SensorEntityDescription):
    """kr_gbus 노선 스케줄 센서 설명."""

    value_fn: Callable[[BusRouteInfoItem, DayType], Any]
    attrs_fn: Callable[[BusRouteInfoItem], dict[str, Any]]


def _time_value(info: BusRouteInfoItem, day_type: DayType, field_prefix: str):
    """요일 구분에 따라 해당하는 time 필드 값을 반환한다."""
    field_map = {
        DayType.WEEKDAY: f"{field_prefix}",
        DayType.SATURDAY: f"sat_{field_prefix}",
        DayType.SUNDAY: f"sun_{field_prefix}",
        DayType.HOLIDAY: f"we_{field_prefix}",
    }
    return getattr(info, field_map[day_type], None)


def _time_attrs(info: BusRouteInfoItem, field_prefix: str) -> dict[str, Any]:
    """모든 요일의 시간 필드를 attribute 딕셔너리로 반환한다."""
    return {
        "평일": getattr(info, field_prefix, None),
        "토요일": getattr(info, f"sat_{field_prefix}", None),
        "일요일": getattr(info, f"sun_{field_prefix}", None),
        "공휴일": getattr(info, f"we_{field_prefix}", None),
    }


SENSOR_DESCRIPTIONS: list[GBusSensorEntityDescription] = [
    # 노선 상태
    GBusSensorEntityDescription(
        key="flag",
        translation_key="flag",
        name="운행상태",
        icon="mdi:bus-alert",
        value_fn=lambda item: item.flag.display_name if item.flag else None,
    ),
    # 첫 번째 버스
    GBusSensorEntityDescription(
        key="arrival_time1",
        translation_key="arrival_time",
        name="도착시간",
        icon="mdi:bus-clock",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda item: item.predict_time1,
    ),
    GBusSensorEntityDescription(
        key="location1",
        translation_key="location",
        name="남은정류장",
        icon="mdi:map-marker-distance",
        native_unit_of_measurement="개",
        value_fn=lambda item: item.location_no1,
    ),
    GBusSensorEntityDescription(
        key="crowded1",
        translation_key="crowded",
        name="혼잡도",
        icon="mdi:account-group",
        value_fn=lambda item: item.crowded1.display_name if item.crowded1 else None,
    ),
    GBusSensorEntityDescription(
        key="remain_seat1",
        translation_key="remain_seat",
        name="잔여좌석",
        icon="mdi:seat-passenger",
        native_unit_of_measurement="석",
        value_fn=lambda item: item.remain_seat_cnt1,
    ),
    GBusSensorEntityDescription(
        key="plate_no1",
        translation_key="plate_no",
        name="차량번호",
        icon="mdi:bus",
        value_fn=lambda item: item.plate_no1,
    ),
    GBusSensorEntityDescription(
        key="low_plate1",
        translation_key="low_plate",
        name="차량유형",
        icon="mdi:wheelchair-accessibility",
        value_fn=lambda item: item.low_plate1.display_name if item.low_plate1 else None,
    ),
    # 두 번째 버스
    GBusSensorEntityDescription(
        key="arrival_time2",
        translation_key="arrival_time_next",
        name="도착시간 (2번째)",
        icon="mdi:bus-clock",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda item: item.predict_time2,
    ),
    GBusSensorEntityDescription(
        key="location2",
        translation_key="location_next",
        name="남은정류장 (2번째)",
        icon="mdi:map-marker-distance",
        native_unit_of_measurement="개",
        value_fn=lambda item: item.location_no2,
    ),
    GBusSensorEntityDescription(
        key="crowded2",
        translation_key="crowded_next",
        name="혼잡도 (2번째)",
        icon="mdi:account-group",
        value_fn=lambda item: item.crowded2.display_name if item.crowded2 else None,
    ),
    GBusSensorEntityDescription(
        key="remain_seat2",
        translation_key="remain_seat_next",
        name="잔여좌석 (2번째)",
        icon="mdi:seat-passenger",
        native_unit_of_measurement="석",
        value_fn=lambda item: item.remain_seat_cnt2,
    ),
    GBusSensorEntityDescription(
        key="plate_no2",
        translation_key="plate_no_next",
        name="차량번호 (2번째)",
        icon="mdi:bus",
        value_fn=lambda item: item.plate_no2,
    ),
    GBusSensorEntityDescription(
        key="low_plate2",
        translation_key="low_plate_next",
        name="차량유형 (2번째)",
        icon="mdi:wheelchair-accessibility",
        value_fn=lambda item: item.low_plate2.display_name if item.low_plate2 else None,
    ),
]

ROUTE_SENSOR_DESCRIPTIONS: list[GBusRouteSensorEntityDescription] = [
    GBusRouteSensorEntityDescription(
        key="up_first_time",
        translation_key="up_first_time",
        name="금일 기점 첫차",
        icon="mdi:bus-clock",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda info, dt: _time_value(info, dt, "up_first_time"),
        attrs_fn=lambda info: _time_attrs(info, "up_first_time"),
    ),
    GBusRouteSensorEntityDescription(
        key="up_last_time",
        translation_key="up_last_time",
        name="금일 기점 막차",
        icon="mdi:bus-clock",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda info, dt: _time_value(info, dt, "up_last_time"),
        attrs_fn=lambda info: _time_attrs(info, "up_last_time"),
    ),
    GBusRouteSensorEntityDescription(
        key="down_first_time",
        translation_key="down_first_time",
        name="금일 종점 첫차",
        icon="mdi:bus-clock",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda info, dt: _time_value(info, dt, "down_first_time"),
        attrs_fn=lambda info: _time_attrs(info, "down_first_time"),
    ),
    GBusRouteSensorEntityDescription(
        key="down_last_time",
        translation_key="down_last_time",
        name="금일 종점 막차",
        icon="mdi:bus-clock",
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=lambda info, dt: _time_value(info, dt, "down_last_time"),
        attrs_fn=lambda info: _time_attrs(info, "down_last_time"),
    ),
]

DAY_TYPE_DESCRIPTION = SensorEntityDescription(
    key="day_type",
    translation_key="day_type",
    name="요일구분",
    icon="mdi:calendar-today",
)
