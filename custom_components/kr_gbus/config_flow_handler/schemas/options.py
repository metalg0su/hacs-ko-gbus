"""options flow 스키마."""

from __future__ import annotations

import voluptuous as vol
from homeassistant.helpers import selector

from ...api.client.bus_station_client import BusStationItem, BusStationViaRouteItem


def get_search_station_schema() -> vol.Schema:
    """정류장 검색 스키마."""
    return vol.Schema(
        {
            vol.Required("keyword"): selector.TextSelector(),
        },
    )


def get_select_station_schema(stations: list[BusStationItem]) -> vol.Schema:
    """정류장 선택 스키마."""
    options = []
    for station in stations:
        mobile = f" [{station.mobile_no}]" if station.mobile_no else ""
        label = f"{station.station_name} ({station.region_name}){mobile}"
        options.append(
            selector.SelectOptionDict(
                value=str(station.station_id),
                label=label,
            ),
        )
    return vol.Schema(
        {
            vol.Required("station"): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                ),
            ),
        },
    )


def get_select_route_schema(routes: list[BusStationViaRouteItem]) -> vol.Schema:
    """노선 선택 스키마."""
    options = []
    for route in routes:
        label = f"{route.route_name} → {route.route_dest_name}"
        options.append(
            selector.SelectOptionDict(
                value=str(route.route_id),
                label=label,
            ),
        )
    return vol.Schema(
        {
            vol.Required("route"): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=options,
                    mode=selector.SelectSelectorMode.DROPDOWN,
                ),
            ),
        },
    )
