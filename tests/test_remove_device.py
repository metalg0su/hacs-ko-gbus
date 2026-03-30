"""async_remove_config_entry_device 테스트."""

from unittest.mock import MagicMock

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.kr_gbus import async_remove_config_entry_device
from custom_components.kr_gbus.const import (
    CONF_API_KEY_ARRIVAL,
    CONF_MONITORS,
    CONF_MONITOR_ROUTE_ID,
    CONF_MONITOR_STA_ORDER,
    CONF_MONITOR_STATION_ID,
    DOMAIN,
)


def _make_monitor(station_id: str, route_id: str, sta_order: str) -> dict:
    return {
        CONF_MONITOR_STATION_ID: station_id,
        CONF_MONITOR_ROUTE_ID: route_id,
        CONF_MONITOR_STA_ORDER: sta_order,
    }


MONITOR_A = _make_monitor("S1", "R1", "1")
MONITOR_B = _make_monitor("S2", "R2", "2")


def _make_config_entry(hass: HomeAssistant, monitors: list[dict]) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_API_KEY_ARRIVAL: "test_key"},
        options={CONF_MONITORS: monitors},
    )
    entry.add_to_hass(hass)
    return entry


def _make_device(identifiers: set) -> MagicMock:
    device = MagicMock(spec=dr.DeviceEntry)
    device.identifiers = identifiers
    return device


async def test_matching_monitor_removed(hass: HomeAssistant):
    """삭제 대상 디바이스의 모니터가 options에서 제거된다."""
    entry = _make_config_entry(hass, [dict(MONITOR_A), dict(MONITOR_B)])
    device = _make_device({(DOMAIN, "S1_R1_1")})

    result = await async_remove_config_entry_device(hass, entry, device)

    assert result is True
    assert entry.options[CONF_MONITORS] == [MONITOR_B]


async def test_no_match_leaves_options_unchanged(hass: HomeAssistant):
    """매칭되지 않는 디바이스면 options를 변경하지 않는다."""
    entry = _make_config_entry(hass, [dict(MONITOR_A), dict(MONITOR_B)])
    device = _make_device({(DOMAIN, "S9_R9_9")})

    result = await async_remove_config_entry_device(hass, entry, device)

    assert result is True
    assert entry.options[CONF_MONITORS] == [MONITOR_A, MONITOR_B]
