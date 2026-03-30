"""kr_gbus 데이터 업데이트 코디네이터."""

from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.util import dt as dt_util
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from ..api import GBusApiClientAuthenticationError, GBusApiClientError
from ..api.client.bus_arrival_client import BusArrivalItem
from ..api.client.bus_route_client import BusRouteInfoItem
from ..api.models import RouteFlag
from ..const import CONF_MONITORS, CONF_MONITOR_ROUTE_ID, CONF_MONITOR_STATION_ID, CONF_MONITOR_STA_ORDER, LOGGER
from ..helpers import get_day_type, get_schedule_times

MonitorKey = tuple[str, str, str]
"""(station_id, route_id, sta_order)"""

GBusCoordinatorData = dict[MonitorKey, BusArrivalItem | None]


class GBusDataUpdateCoordinator(DataUpdateCoordinator[GBusCoordinatorData]):
    """API 데이터 갱신을 관리하는 코디네이터."""

    config_entry: "GBusConfigEntry"  # noqa: F821 - 순환참조 방지

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._route_schedules: dict[str, BusRouteInfoItem | None] = {}
        self._route_schedules_loaded: bool = False
        self._default_update_interval: timedelta | None = self.update_interval

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

    def _is_station_stopped(
        self, station_keys: list[MonitorKey], prev_data: GBusCoordinatorData | None
    ) -> bool:
        """직전 응답 기준으로 정류장의 모든 노선이 운행 종료인지 판별한다.

        직전 데이터가 없거나, 항목이 None이면 안전하게 False(호출 필요)를 반환한다.
        """
        if not prev_data:
            return False
        for key in station_keys:
            item = prev_data.get(key)
            if item is None or item.flag != RouteFlag.운행종료:
                return False
        return True

    def _get_next_resume_time(self, keys: list[MonitorKey], now: datetime) -> datetime | None:
        """다음날 가장 이른 첫차 시간을 반환한다."""
        tomorrow = now.date() + timedelta(days=1)
        tomorrow_day_type = get_day_type(tomorrow)

        earliest = None
        for route_id in {key[1] for key in keys}:
            info = self._route_schedules.get(route_id)
            if info is None:
                continue
            first, _ = get_schedule_times(info, tomorrow_day_type)
            if first is not None and (earliest is None or first < earliest):
                earliest = first

        if earliest is None:
            return None
        return datetime.combine(tomorrow, earliest)

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

        arrival = self.config_entry.runtime_data.arrival
        result: GBusCoordinatorData = {}
        all_skipped = True

        for station_id, station_keys in stations.items():
            # 직전 응답에서 모든 노선이 운행종료면 스킵 (이전 데이터 유지)
            if self._is_station_stopped(station_keys, prev_data):
                LOGGER.debug("운행 종료 스킵: station_id=%s", station_id)
                for key in station_keys:
                    result[key] = prev_data[key]
                continue

            all_skipped = False

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

            # 응답을 (station_id, route_id, sta_order) 키로 인덱싱
            items_by_key: dict[MonitorKey, BusArrivalItem] = {}
            if response.bus_arrival_list:
                for item in response.bus_arrival_list:
                    item_key: MonitorKey = (
                        str(item.station_id),
                        str(item.route_id),
                        str(item.sta_order),
                    )
                    items_by_key[item_key] = item

            for key in station_keys:
                result[key] = items_by_key.get(key)

        # update_interval 동적 변경
        if all_skipped and keys:
            next_resume = self._get_next_resume_time(keys, now)
            if next_resume:
                sleep_duration = next_resume - now
                self.update_interval = sleep_duration
                LOGGER.info(
                    "모든 노선 운행 종료. 다음 갱신: %s (%s 후)",
                    next_resume.strftime("%Y-%m-%d %H:%M"),
                    sleep_duration,
                )
        elif self.update_interval != self._default_update_interval:
            self.update_interval = self._default_update_interval
            LOGGER.info("운행 재개. 갱신 주기 복원: %s", self._default_update_interval)

        return result
