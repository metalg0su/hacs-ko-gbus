"""kr_gbus options flow 핸들러."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import OptionsFlowWithConfigEntry
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from ..api import GBusApiClientError
from ..api.client.bus_station_client import (
    BusStationApiClient,
    BusStationItem,
    BusStationViaRouteItem,
)
from ..const import (
    CONF_API_KEY_ARRIVAL,
    CONF_MONITORS,
    CONF_MONITOR_ROUTE_ID,
    CONF_MONITOR_STATION_ID,
    CONF_MONITOR_STA_ORDER,
    LOGGER,
)
from .schemas.options import (
    get_search_station_schema,
    get_select_route_schema,
    get_select_station_schema,
)


class GBusOptionsFlowHandler(OptionsFlowWithConfigEntry):
    """kr_gbus 옵션 플로우. 모니터 추가 전용."""

    def __init__(self, config_entry) -> None:
        """초기화."""
        super().__init__(config_entry)
        self._station_client: BusStationApiClient | None = None
        self._stations: list[BusStationItem] = []
        self._selected_station: BusStationItem | None = None
        self._via_routes: list[BusStationViaRouteItem] = []

    def _get_station_client(self) -> BusStationApiClient:
        """BusStationApiClient를 생성하거나 캐시된 인스턴스를 반환한다."""
        if self._station_client is None:
            self._station_client = BusStationApiClient(
                service_key=self.config_entry.data[CONF_API_KEY_ARRIVAL],
                session=async_get_clientsession(self.hass),
            )
        return self._station_client

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """진입점 — 바로 정류장 검색으로 이동."""
        return await self.async_step_search_station()

    async def async_step_search_station(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """정류장 이름 검색."""
        if user_input is None:
            return self.async_show_form(
                step_id="search_station",
                data_schema=get_search_station_schema(),
            )

        keyword = user_input["keyword"]
        client = self._get_station_client()

        try:
            response = await client.async_get_bus_station_list(keyword)
        except GBusApiClientError:
            LOGGER.warning("정류장 검색 실패: %s", keyword)
            return self.async_show_form(
                step_id="search_station",
                data_schema=get_search_station_schema(),
                errors={"base": "connection"},
            )

        if not response.bus_station_list:
            return self.async_show_form(
                step_id="search_station",
                data_schema=get_search_station_schema(),
                errors={"base": "no_results"},
            )

        self._stations = response.bus_station_list
        return await self.async_step_select_station()

    async def async_step_select_station(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """검색 결과에서 정류장 선택."""
        if user_input is None:
            return self.async_show_form(
                step_id="select_station",
                data_schema=get_select_station_schema(self._stations),
            )

        station_id = user_input["station"]
        self._selected_station = next(
            s for s in self._stations if str(s.station_id) == station_id
        )

        client = self._get_station_client()
        try:
            response = await client.async_get_bus_station_via_route_list(
                station_id
            )
        except GBusApiClientError:
            LOGGER.warning("경유 노선 조회 실패: %s", station_id)
            return self.async_show_form(
                step_id="select_station",
                data_schema=get_select_station_schema(self._stations),
                errors={"base": "connection"},
            )

        if not response.bus_route_list:
            return self.async_show_form(
                step_id="select_station",
                data_schema=get_select_station_schema(self._stations),
                errors={"base": "no_routes"},
            )

        self._via_routes = response.bus_route_list
        return await self.async_step_select_route()

    async def async_step_select_route(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """노선 선택."""
        if user_input is None:
            return self.async_show_form(
                step_id="select_route",
                data_schema=get_select_route_schema(self._via_routes),
            )

        route_id = user_input["route"]
        selected_route = next(
            r for r in self._via_routes if str(r.route_id) == route_id
        )

        monitor = {
            CONF_MONITOR_STATION_ID: str(self._selected_station.station_id),
            CONF_MONITOR_ROUTE_ID: str(selected_route.route_id),
            CONF_MONITOR_STA_ORDER: str(selected_route.sta_order),
            "station_name": self._selected_station.station_name,
            "route_name": selected_route.route_name,
        }

        # 중복 체크
        monitors = list(self.config_entry.options.get(CONF_MONITORS, []))
        for existing in monitors:
            if (
                existing[CONF_MONITOR_STATION_ID] == monitor[CONF_MONITOR_STATION_ID]
                and existing[CONF_MONITOR_ROUTE_ID] == monitor[CONF_MONITOR_ROUTE_ID]
                and existing[CONF_MONITOR_STA_ORDER] == monitor[CONF_MONITOR_STA_ORDER]
            ):
                return self.async_show_form(
                    step_id="select_route",
                    data_schema=get_select_route_schema(self._via_routes),
                    errors={"base": "duplicate_monitor"},
                )

        monitors.append(monitor)
        return self.async_create_entry(data={CONF_MONITORS: monitors})
