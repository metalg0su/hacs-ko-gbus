"""kr_gbus 센서 플랫폼."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from ..const import (
    CONF_MONITORS,
    CONF_MONITOR_ROUTE_ID,
    CONF_MONITOR_STATION_ID,
    CONF_MONITOR_STA_ORDER,
)
from ..coordinator import MonitorKey
from ..data import GBusConfigEntry
from .descriptions import ROUTE_SENSOR_DESCRIPTIONS, SENSOR_DESCRIPTIONS
from .sensors import GBusArrivalSensor, GBusDayTypeSensor, GBusRouteSensor


def _all_sensor_keys(
    entry_id: str,
    monitors: list[dict[str, str]],
) -> set[str]:
    """현재 모니터 설정에서 생성될 모든 센서의 unique_id를 반환한다."""
    keys: set[str] = set()
    for m in monitors:
        prefix = f"{entry_id}_{m[CONF_MONITOR_STATION_ID]}_{m[CONF_MONITOR_ROUTE_ID]}_{m[CONF_MONITOR_STA_ORDER]}"
        for desc in SENSOR_DESCRIPTIONS:
            keys.add(f"{prefix}_{desc.key}")
        for desc in ROUTE_SENSOR_DESCRIPTIONS:
            keys.add(f"{prefix}_{desc.key}")
    keys.add(f"{entry_id}_day_type")
    return keys


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GBusConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """센서 엔티티를 설정한다."""
    coordinator = entry.runtime_data.coordinator
    monitors = entry.options.get(CONF_MONITORS, [])

    # 현재 모니터에 없는 stale 엔티티를 registry에서 제거
    current_unique_ids = _all_sensor_keys(entry.entry_id, monitors)

    registry = er.async_get(hass)
    for entity_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
        if entity_entry.unique_id not in current_unique_ids:
            registry.async_remove(entity_entry.entity_id)

    entities: list[SensorEntity] = []

    # 요일 구분 센서 (config entry당 1개)
    entities.append(GBusDayTypeSensor(coordinator))

    for monitor in monitors:
        key: MonitorKey = (
            monitor[CONF_MONITOR_STATION_ID],
            monitor[CONF_MONITOR_ROUTE_ID],
            monitor[CONF_MONITOR_STA_ORDER],
        )
        # 도착정보 센서
        for desc in SENSOR_DESCRIPTIONS:
            entities.append(GBusArrivalSensor(coordinator, desc, key, monitor))
        # 노선 스케줄 센서
        for desc in ROUTE_SENSOR_DESCRIPTIONS:
            entities.append(GBusRouteSensor(coordinator, desc, key, monitor))

    async_add_entities(entities)
