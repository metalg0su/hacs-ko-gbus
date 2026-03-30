"""kr_gbus 데이터 업데이트 코디네이터."""

from __future__ import annotations

from datetime import datetime

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from ..api import GBusApiClientAuthenticationError, GBusApiClientError
from ..api.client.bus_arrival_client import BusArrivalItem
from ..api.client.bus_route_client import BusRouteInfoItem
from ..api.models import RouteFlag
from ..const import CONF_MONITORS, CONF_MONITOR_ROUTE_ID, CONF_MONITOR_STATION_ID, CONF_MONITOR_STA_ORDER, LOGGER
from ..helpers import get_day_type, get_schedule_times, is_operating

MonitorKey = tuple[str, str, str]
"""(station_id, route_id, sta_order)"""

GBusCoordinatorData = dict[MonitorKey, BusArrivalItem | None]


def is_station_stopped(
    station_keys: list[MonitorKey],
    prev_data: GBusCoordinatorData,
    route_schedules: dict[str, BusRouteInfoItem | None],
    now: datetime,
) -> bool:
    """운행 종료 상태이고 비운행 시간대이면 True."""
    for key in station_keys:
        item = prev_data.get(key)
        if item is None or item.flag != RouteFlag.운행종료:
            return False

    route_ids = {key[1] for key in station_keys}
    today_type = get_day_type(now.date())
    for route_id in route_ids:
        info = route_schedules.get(route_id)
        if info is None:
            return False
        first, last = get_schedule_times(info, today_type)
        if is_operating(first, last, now.time()):
            return False

    return True


class GBusDataUpdateCoordinator(DataUpdateCoordinator[GBusCoordinatorData]):
    """API 데이터 갱신을 관리하는 코디네이터."""

    config_entry: "GBusConfigEntry"  # noqa: F821 - 순환참조 방지

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._route_schedules: dict[str, BusRouteInfoItem | None] = {}
        self._route_schedules_loaded: bool = False

    @property
    def route_schedules(self) -> dict[str, BusRouteInfoItem | None]:
        """캐싱된 노선 스케줄 정보."""
        return self._route_schedules

    def _get_monitor_keys(self) -> list[MonitorKey]:
        """config entry options에서 모니터 키 목록을 읽는다."""
        monitors = self.config_entry.options.get(CONF_MONITORS, [])
        return [
            (m[CONF_MONITOR_STATION_ID], m[CONF_MONITOR_ROUTE_ID], m[CONF_MONITOR_STA_ORDER])
            for m in monitors
        ]

    async def _load_route_schedules(self, keys: list[MonitorKey]) -> None:
        """모니터링 중인 노선의 상세 정보를 1회 조회하여 캐싱한다."""
        route_ids = {key[1] for key in keys}
        route_client = self.config_entry.runtime_data.route

        for route_id in route_ids:
            if route_id in self._route_schedules:
                continue
            try:
                resp = await route_client.async_get_bus_route_info_item(route_id)
                self._route_schedules[route_id] = resp.bus_route_info_item
                LOGGER.debug("노선 스케줄 로드: route_id=%s", route_id)
            except Exception:
                LOGGER.warning("노선 스케줄 조회 실패: route_id=%s", route_id, exc_info=True)
                self._route_schedules[route_id] = None

        self._route_schedules_loaded = True

    async def _fetch_station_arrivals(
        self, station_id: str, station_keys: list[MonitorKey],
    ) -> dict[MonitorKey, BusArrivalItem | None]:
        """정류장 1개의 도착정보를 조회하여 MonitorKey별로 매핑한다."""
        arrival = self.config_entry.runtime_data.arrival

        try:
            response = await arrival.async_get_bus_arrival_list(station_id)
        except GBusApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(
                translation_domain="kr_gbus",
                translation_key="authentication_failed",
            ) from exception
        except GBusApiClientError as exception:
            raise UpdateFailed(
                translation_domain="kr_gbus",
                translation_key="update_failed",
            ) from exception

        items_by_key: dict[MonitorKey, BusArrivalItem] = {}
        if response.bus_arrival_list:
            for item in response.bus_arrival_list:
                item_key: MonitorKey = (
                    str(item.station_id),
                    str(item.route_id),
                    str(item.sta_order),
                )
                items_by_key[item_key] = item

        return {key: items_by_key.get(key) for key in station_keys}

    async def _async_update_data(self) -> GBusCoordinatorData:
        """API에서 도착정보를 가져온다."""
        keys = self._get_monitor_keys()
        if not keys:
            return {}

        # 노선 스케줄 1회 로드
        if not self._route_schedules_loaded:
            await self._load_route_schedules(keys)

        now = dt_util.now()
        prev_data = self.data

        # station_id 기준 그룹핑 → 정류장당 API 1회 호출
        stations: dict[str, list[MonitorKey]] = {}
        for key in keys:
            stations.setdefault(key[0], []).append(key)

        result: GBusCoordinatorData = {}

        is_data_ready: bool = prev_data and self._route_schedules_loaded
        for station_id, station_keys in stations.items():
            if is_data_ready and is_station_stopped(station_keys, prev_data, self._route_schedules, now):
                LOGGER.debug("운행 종료 스킵: station_id=%s", station_id)
                for key in station_keys:
                    result[key] = prev_data[key]
                continue

            result.update(await self._fetch_station_arrivals(station_id, station_keys))

        return result
