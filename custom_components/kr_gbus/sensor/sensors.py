"""센서 엔티티 클래스."""

from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Any

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.util import dt as dt_util

from ..api.client.bus_route_client import BusRouteInfoItem
from ..const import DOMAIN
from ..coordinator import GBusDataUpdateCoordinator, MonitorKey
from ..entity import GBusEntity
from ..helpers import get_day_type
from .descriptions import (
    DAY_TYPE_DESCRIPTION,
    GBusRouteSensorEntityDescription,
    GBusSensorEntityDescription,
)


def _make_device_info(monitor_key: MonitorKey, monitor: dict[str, str]) -> DeviceInfo:
    """모니터 키와 monitor dict로 DeviceInfo를 생성한다."""
    station_id, route_id, sta_order = monitor_key
    station_name = monitor.get("station_name", station_id)
    route_name = monitor.get("route_name", route_id)
    route_dest_name = monitor.get("route_dest_name")
    name = f"{station_name} / {route_name}"
    if route_dest_name:
        name = f"{station_name} / {route_name} → {route_dest_name}"
    return DeviceInfo(
        identifiers={(DOMAIN, f"{station_id}_{route_id}_{sta_order}")},
        name=name,
    )


def _make_unique_id(
    coordinator: GBusDataUpdateCoordinator,
    monitor_key: MonitorKey,
    key: str,
) -> str:
    """센서 unique_id를 생성한다."""
    station_id, route_id, sta_order = monitor_key
    return (
        f"{coordinator.config_entry.entry_id}"
        f"_{station_id}_{route_id}_{sta_order}"
        f"_{key}"
    )


class GBusArrivalSensor(GBusEntity, SensorEntity):
    """버스 도착정보 센서."""

    entity_description: GBusSensorEntityDescription

    def __init__(
        self,
        coordinator: GBusDataUpdateCoordinator,
        entity_description: GBusSensorEntityDescription,
        monitor_key: MonitorKey,
        monitor: dict[str, str],
    ) -> None:
        super().__init__(coordinator, entity_description)
        self._monitor_key = monitor_key
        self._route_dest_name = monitor.get("route_dest_name")
        self._attr_unique_id = _make_unique_id(coordinator, monitor_key, entity_description.key)
        self._attr_device_info = _make_device_info(monitor_key, monitor)

    @property
    def available(self) -> bool:
        """데이터가 있을 때만 available."""
        return (
            super().available
            and self.coordinator.data is not None
            and self._monitor_key in self.coordinator.data
            and self.coordinator.data[self._monitor_key] is not None
        )

    @property
    def native_value(self) -> Any | None:
        """센서 값."""
        if not self.coordinator.data:
            return None
        item = self.coordinator.data.get(self._monitor_key)
        if item is None:
            return None
        value = self.entity_description.value_fn(item)
        if self.entity_description.device_class == SensorDeviceClass.TIMESTAMP and value is not None:
            return self.coordinator.last_update_success_time + timedelta(minutes=value)
        return value

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """진행방향(종점명)을 attribute로 노출."""
        if self._route_dest_name:
            return {"route_dest_name": self._route_dest_name}
        return None


class GBusRouteSensor(GBusEntity, SensorEntity):
    """노선 스케줄 센서 (첫차/막차)."""

    entity_description: GBusRouteSensorEntityDescription

    def __init__(
        self,
        coordinator: GBusDataUpdateCoordinator,
        entity_description: GBusRouteSensorEntityDescription,
        monitor_key: MonitorKey,
        monitor: dict[str, str],
    ) -> None:
        super().__init__(coordinator, entity_description)
        self._monitor_key = monitor_key
        self._route_id = monitor_key[1]
        self._attr_unique_id = _make_unique_id(coordinator, monitor_key, entity_description.key)
        self._attr_device_info = _make_device_info(monitor_key, monitor)

    def _get_route_info(self) -> BusRouteInfoItem | None:
        """캐싱된 노선 정보를 반환한다."""
        return self.coordinator.route_schedules.get(self._route_id)

    @property
    def available(self) -> bool:
        """노선 정보가 있을 때만 available."""
        return super().available and self._get_route_info() is not None

    @property
    def native_value(self) -> Any | None:
        """오늘 요일 기준 시간 값."""
        info = self._get_route_info()
        if info is None:
            return None
        day_type = get_day_type(dt_util.now().date())
        value = self.entity_description.value_fn(info, day_type)
        if isinstance(value, time):
            return datetime.combine(dt_util.now().date(), value, tzinfo=dt_util.now().tzinfo)
        return value

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """모든 요일의 시간을 attribute로 노출."""
        info = self._get_route_info()
        if info is None:
            return None
        return self.entity_description.attrs_fn(info)


class GBusDayTypeSensor(GBusEntity, SensorEntity):
    """요일 구분 센서 (config entry당 1개)."""

    def __init__(
        self,
        coordinator: GBusDataUpdateCoordinator,
    ) -> None:
        super().__init__(coordinator, DAY_TYPE_DESCRIPTION)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_day_type"

    @property
    def native_value(self) -> str:
        """오늘의 요일 구분."""
        return get_day_type(dt_util.now().date()).value
