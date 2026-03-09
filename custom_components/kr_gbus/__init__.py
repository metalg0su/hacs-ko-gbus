"""경기버스정보 통합."""

from datetime import timedelta

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import BusArrivalApiClient, BusRouteApiClient
from .const import (
    CONF_API_KEY_ARRIVAL,
    CONF_MONITORS,
    CONF_MONITOR_ROUTE_ID,
    CONF_MONITOR_STATION_ID,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL_SECONDS,
    DOMAIN,
    LOGGER,
)
from .coordinator import GBusDataUpdateCoordinator
from .data import GBusConfigEntry, GBusData

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GBusConfigEntry,
) -> bool:
    """설정 항목을 로드한다."""
    session = async_get_clientsession(hass)
    service_key = entry.data[CONF_API_KEY_ARRIVAL]

    arrival = BusArrivalApiClient(service_key=service_key, session=session)
    route = BusRouteApiClient(service_key=service_key, session=session)

    coordinator = GBusDataUpdateCoordinator(
        hass=hass,
        logger=LOGGER,
        name=DOMAIN,
        config_entry=entry,
        update_interval=timedelta(
            seconds=int(entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL_SECONDS)),
        ),
        always_update=False,
    )

    entry.runtime_data = GBusData(
        arrival=arrival,
        route=route,
        coordinator=coordinator,
    )

    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_options_updated))

    return True


async def _async_options_updated(
    hass: HomeAssistant,
    entry: GBusConfigEntry,
) -> None:
    """Options 변경 시 통합을 다시 로드한다."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(
    hass: HomeAssistant,
    entry: GBusConfigEntry,
) -> bool:
    """설정 항목을 언로드한다."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_remove_config_entry_device(
    hass: HomeAssistant,
    entry: GBusConfigEntry,
    device_entry: dr.DeviceEntry,
) -> bool:
    """디바이스 삭제 시 해당 모니터를 options에서 제거한다."""
    monitors = list(entry.options.get(CONF_MONITORS, []))

    # device identifiers: {(DOMAIN, "{station_id}_{route_id}")}
    updated = [
        m for m in monitors
        if (DOMAIN, f"{m[CONF_MONITOR_STATION_ID]}_{m[CONF_MONITOR_ROUTE_ID]}")
        not in device_entry.identifiers
    ]

    if len(updated) != len(monitors):
        hass.config_entries.async_update_entry(
            entry, options={CONF_MONITORS: updated}
        )

    return True
